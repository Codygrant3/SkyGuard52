#include "SkyguardPsoStableKeyFilterCommandlet.h"

#if WITH_EDITOR
#include "HAL/FileManager.h"
#include "PipelineCacheUtilities.h"
#include "PipelineFileCache.h"
#include "ShaderCodeLibrary.h"
#endif

USkyguardPsoStableKeyFilterCommandlet::USkyguardPsoStableKeyFilterCommandlet()
{
	IsClient = false;
	IsEditor = true;
	IsServer = false;
	LogToConsole = true;
}

int32 USkyguardPsoStableKeyFilterCommandlet::Main(const FString& Params)
{
#if !WITH_EDITOR
	UE_LOG(LogTemp, Error, TEXT("SkyguardPsoStableKeyFilter requires an editor build."));
	return 1;
#else
	TArray<FString> Tokens;
	TArray<FString> Switches;
	TMap<FString, FString> ParamValues;
	ParseCommandLine(*Params, Tokens, Switches, ParamValues);

	const FString* CaptureDirectory = ParamValues.Find(TEXT("CaptureDir"));
	const FString* InputKeyDirectory = ParamValues.Find(TEXT("InputKeyDir"));
	const FString* OutputFile = ParamValues.Find(TEXT("Output"));
	const FString ShaderFormat = ParamValues.FindRef(TEXT("ShaderFormat"));
	if (!CaptureDirectory || !InputKeyDirectory || !OutputFile || ShaderFormat.IsEmpty())
	{
		UE_LOG(
			LogTemp,
			Error,
			TEXT("Usage: -CaptureDir=<dir> -InputKeyDir=<dir> -Output=<file.shk> -ShaderFormat=PCD3D_SM6"));
		return 2;
	}

	TArray<FString> CaptureFiles;
	IFileManager::Get().FindFilesRecursive(
		CaptureFiles,
		**CaptureDirectory,
		TEXT("*.rec.upipelinecache"),
		true,
		false);
	CaptureFiles.Sort();
	if (CaptureFiles.IsEmpty())
	{
		UE_LOG(LogTemp, Error, TEXT("No recorded PSO caches found under %s."), **CaptureDirectory);
		return 3;
	}

	TSet<FShaderHash> ReferencedShaderHashes;
	int32 LoadedPsoCount = 0;
	for (const FString& CaptureFile : CaptureFiles)
	{
		TSet<FPipelineCacheFileFormatPSO> Psos;
		if (!FPipelineFileCacheManager::LoadPipelineFileCacheInto(CaptureFile, Psos))
		{
			UE_LOG(LogTemp, Error, TEXT("Failed to load recorded PSO cache %s."), *CaptureFile);
			return 4;
		}

		LoadedPsoCount += Psos.Num();
		for (const FPipelineCacheFileFormatPSO& Pso : Psos)
		{
			switch (Pso.Type)
			{
			case FPipelineCacheFileFormatPSO::DescriptorType::Compute:
				ReferencedShaderHashes.Add(Pso.ComputeDesc.ComputeShader);
				break;
			case FPipelineCacheFileFormatPSO::DescriptorType::Graphics:
				ReferencedShaderHashes.Add(Pso.GraphicsDesc.VertexShader);
				ReferencedShaderHashes.Add(Pso.GraphicsDesc.MeshShader);
				ReferencedShaderHashes.Add(Pso.GraphicsDesc.AmplificationShader);
				ReferencedShaderHashes.Add(Pso.GraphicsDesc.FragmentShader);
				ReferencedShaderHashes.Add(Pso.GraphicsDesc.GeometryShader);
				break;
			case FPipelineCacheFileFormatPSO::DescriptorType::RayTracing:
				ReferencedShaderHashes.Add(Pso.RayTracingDesc.ShaderHash);
				break;
			default:
				UE_LOG(LogTemp, Error, TEXT("Unexpected PSO descriptor type in %s."), *CaptureFile);
				return 5;
			}
		}
	}
	ReferencedShaderHashes.Remove(FShaderHash());

	TArray<FString> InputKeyFiles;
	IFileManager::Get().FindFilesRecursive(
		InputKeyFiles,
		**InputKeyDirectory,
		*FString::Printf(TEXT("*%s.shk"), *ShaderFormat),
		true,
		false);
	InputKeyFiles.Sort();
	if (InputKeyFiles.IsEmpty())
	{
		UE_LOG(LogTemp, Error, TEXT("No %s stable-key files found under %s."), *ShaderFormat, **InputKeyDirectory);
		return 6;
	}

	TArray<FStableShaderKeyAndValue> InputKeys;
	for (const FString& InputKeyFile : InputKeyFiles)
	{
		if (!UE::PipelineCacheUtilities::LoadStableKeysFile(InputKeyFile, InputKeys))
		{
			UE_LOG(LogTemp, Error, TEXT("Failed to load stable-key file %s."), *InputKeyFile);
			return 7;
		}
	}

	const FName RequiredPlatform(*ShaderFormat);
	FStableShaderSet FilteredKeys;
	int32 UnsupportedLongPathKeys = 0;
	for (const FStableShaderKeyAndValue& Key : InputKeys)
	{
		if (Key.TargetPlatform == RequiredPlatform && ReferencedShaderHashes.Contains(Key.OutputHash))
		{
			// UE 5.8 saves this count after casting to int8, while validating only
			// that it is below 256. The corresponding loader also reads int8, so
			// values above MAX_int8 become negative and corrupt the binary stream.
			if (Key.ClassNameAndObjectPath.ObjectClassAndPath.Num() > MAX_int8)
			{
				++UnsupportedLongPathKeys;
				continue;
			}
			FilteredKeys.Add(MakeUnique<FStableShaderKeyAndValue>(Key));
		}
	}

	if (FilteredKeys.IsEmpty())
	{
		UE_LOG(LogTemp, Error, TEXT("No stable keys matched the recorded PSO shader hashes."));
		return 8;
	}
	if (!UE::PipelineCacheUtilities::SaveStableKeysFile(*OutputFile, FilteredKeys))
	{
		UE_LOG(LogTemp, Error, TEXT("Failed to save filtered stable-key file %s."), **OutputFile);
		return 9;
	}

	UE_LOG(
		LogTemp,
		Display,
		TEXT("[SkyguardPSOFilter] PASS captures=%d loaded_psos=%d referenced_hashes=%d input_keys=%d output_keys=%d skipped_long_paths=%d output=%s"),
		CaptureFiles.Num(),
		LoadedPsoCount,
		ReferencedShaderHashes.Num(),
		InputKeys.Num(),
		FilteredKeys.Num(),
		UnsupportedLongPathKeys,
		**OutputFile);
	return 0;
#endif
}
