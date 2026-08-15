#include "SkyguardMission01EnvironmentAuthoringLibrary.h"

#include "SkyguardMission01EnvironmentDirector.h"
#include "AssetCompilingManager.h"
#include "Components/SceneCaptureComponent2D.h"
#include "DynamicRHI.h"
#include "Landscape.h"
#include "LandscapeComponent.h"
#include "MaterialShared.h"
#include "Materials/MaterialInstance.h"
#include "RHI.h"
#include "RHIStrings.h"
#include "RenderingThread.h"
#include "ShaderCompiler.h"
#include "ShowFlags.h"

#if WITH_EDITOR

#include "AssetRegistry/AssetRegistryModule.h"
#include "Elements/PCGDataFromActor.h"
#include "Elements/PCGDensityFilter.h"
#include "Elements/PCGDifferenceElement.h"
#include "Elements/PCGStaticMeshSpawner.h"
#include "Elements/PCGSurfaceSampler.h"
#include "Elements/PCGTransformPoints.h"
#include "Elements/PCGTypedGetter.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "EngineUtils.h"
#include "LandscapeProxy.h"
#include "MeshSelectors/PCGMeshSelectorWeighted.h"
#include "Misc/FileHelper.h"
#include "Misc/PackageName.h"
#include "Modules/ModuleManager.h"
#include "PCGCommon.h"
#include "PCGComponent.h"
#include "PCGGraph.h"
#include "PCGNode.h"
#include "UObject/Package.h"

namespace
{
	constexpr int32 HeightmapWidth = 505;
	constexpr int32 HeightmapHeight = 127;
	constexpr int32 ExpectedHeightmapBytes =
		HeightmapWidth * HeightmapHeight * sizeof(uint16);
	const FName LandscapeTag =
		TEXT("Skyguard.Environment.Mission01.Landscape");
	const FName InclusionTag = TEXT("Skyguard.PCG.Inclusion");
	const FName ExclusionTag = TEXT("Skyguard.PCG.Exclusion");

	template <typename TSettings>
	UPCGNode* AddGovernedNode(
		UPCGGraph* Graph,
		TSettings*& OutSettings,
		const TCHAR* Title,
		const int32 X,
		const int32 Y)
	{
		UPCGNode* Node = Graph
			? Graph->AddNodeOfType<TSettings>(OutSettings)
			: nullptr;
		if (Node)
		{
			Node->SetNodeTitle(FName(Title), false);
			Node->SetNodePosition(X, Y);
		}
		return Node;
	}

	void ConfigureSelfComponentSelector(
		UPCGDataFromActorSettings* Settings,
		const FName ComponentTag,
		const int32 Seed)
	{
		Settings->ActorSelector.ActorFilter = EPCGActorFilter::Self;
		Settings->ComponentSelector.ComponentSelection =
			EPCGComponentSelection::ByTag;
		Settings->ComponentSelector.ComponentSelectionTag = ComponentTag;
		Settings->Mode = EPCGGetDataFromActorMode::ParseActorComponents;
		Settings->bIgnorePCGGeneratedComponents = true;
		Settings->Seed = Seed;
	}

	struct FContractCamera
	{
		FVector Location;
		FRotator Rotation;
	};

	const FContractCamera ContractCameras[] = {
		{FVector(25200.f, -8000.f, 10000.f), FRotator(-25.226895f, 90.f, 0.f)},
		{FVector(25200.f, 4000.f, 1200.f), FRotator(-8.530766f, 90.f, 0.f)},
		{FVector(-5000.f, 13300.f, 1500.f), FRotator(-3.433630f, 0.f, 0.f)},
		{FVector(25200.f, 5000.f, 3000.f), FRotator(-19.872176f, 90.f, 0.f)},
		{FVector(25200.f, 13300.f, 30000.f), FRotator(-90.f, 90.f, 0.f)},
	};

	bool DoesBoundsIntersectContractCamera(
		const FBox& Bounds,
		const FContractCamera& Camera)
	{
		const FVector Forward = Camera.Rotation.Vector().GetSafeNormal();
		const FVector End = Camera.Location + Forward * 1000000.f;
		if (FMath::LineBoxIntersection(
			Bounds,
			Camera.Location,
			End,
			End - Camera.Location))
		{
			return true;
		}

		const FRotationMatrix RotationMatrix(Camera.Rotation);
		const FVector Right =
			RotationMatrix.GetScaledAxis(EAxis::Y).GetSafeNormal();
		const FVector Up =
			RotationMatrix.GetScaledAxis(EAxis::Z).GetSafeNormal();
		constexpr float HorizontalFovDegrees = 90.f;
		constexpr float AspectRatio = 16.f / 9.f;
		const float HorizontalTangent =
			FMath::Tan(FMath::DegreesToRadians(HorizontalFovDegrees * 0.5f));
		const float VerticalTangent = HorizontalTangent / AspectRatio;
		const FVector Minimum = Bounds.Min;
		const FVector Maximum = Bounds.Max;
		for (int32 CornerIndex = 0; CornerIndex < 8; ++CornerIndex)
		{
			const FVector Corner(
				(CornerIndex & 1) ? Maximum.X : Minimum.X,
				(CornerIndex & 2) ? Maximum.Y : Minimum.Y,
				(CornerIndex & 4) ? Maximum.Z : Minimum.Z);
			const FVector Relative = Corner - Camera.Location;
			const float Depth = FVector::DotProduct(Relative, Forward);
			if (Depth <= 10.f)
			{
				continue;
			}
			if (FMath::Abs(FVector::DotProduct(Relative, Right))
					<= Depth * HorizontalTangent
				&& FMath::Abs(FVector::DotProduct(Relative, Up))
					<= Depth * VerticalTangent)
			{
				return true;
			}
		}
		return false;
	}
}

#endif

FString USkyguardMission01EnvironmentAuthoringLibrary::
GetActiveRHIAndFeatureLevel()
{
	const FString RHIName =
		GDynamicRHI ? FString(GDynamicRHI->GetName()) : TEXT("Unavailable");
	return FString::Printf(
		TEXT("%s|%s"),
		*RHIName,
		*LexToString(GMaxRHIFeatureLevel));
}

FSkyguardMission01EnvironmentAuthoringResult
USkyguardMission01EnvironmentAuthoringLibrary::
AuthorGovernedLandscapeAndGraph(
	ASkyguardMission01EnvironmentDirector* Director,
	const FString& HeightmapSourcePath,
	const FString& GraphPackagePath)
{
	FSkyguardMission01EnvironmentAuthoringResult Result;

#if !WITH_EDITOR
	Result.Error = TEXT("The governed authoring bridge is editor-only.");
	return Result;
#else
	if (!Director || !Director->GetWorld())
	{
		Result.Error = TEXT("A director in a valid editor world is required.");
		return Result;
	}
	if (!FPackageName::IsValidLongPackageName(GraphPackagePath))
	{
		Result.Error = FString::Printf(
			TEXT("Invalid graph package path: %s"), *GraphPackagePath);
		return Result;
	}
	if (FPackageName::DoesPackageExist(GraphPackagePath)
		|| FindObject<UPCGGraph>(
			nullptr,
			*(GraphPackagePath + TEXT(".")
				+ FPackageName::GetLongPackageAssetName(GraphPackagePath))))
	{
		Result.Error = FString::Printf(
			TEXT("Immutable graph package already exists: %s"),
			*GraphPackagePath);
		return Result;
	}

	TArray<uint8> HeightBytes;
	if (!FFileHelper::LoadFileToArray(HeightBytes, *HeightmapSourcePath))
	{
		Result.Error = FString::Printf(
			TEXT("Could not load governed height source: %s"),
			*HeightmapSourcePath);
		return Result;
	}
	if (HeightBytes.Num() != ExpectedHeightmapBytes)
	{
		Result.Error = FString::Printf(
			TEXT("Height source bytes=%d; expected=%d."),
			HeightBytes.Num(),
			ExpectedHeightmapBytes);
		return Result;
	}

	for (TActorIterator<ALandscape> It(Director->GetWorld()); It; ++It)
	{
		if (It->ActorHasTag(LandscapeTag)
			|| It->GetActorLabel()
				== TEXT("M01_P4_Landscape_Production"))
		{
			Result.Error =
				TEXT("Immutable target world already contains governed Landscape.");
			return Result;
		}
	}

	TArray<uint16> HeightSamples;
	HeightSamples.SetNumUninitialized(HeightmapWidth * HeightmapHeight);
	for (int32 Index = 0; Index < HeightSamples.Num(); ++Index)
	{
		const int32 ByteIndex = Index * 2;
		HeightSamples[Index] =
			static_cast<uint16>(HeightBytes[ByteIndex])
			| (static_cast<uint16>(HeightBytes[ByteIndex + 1]) << 8);
	}

	FActorSpawnParameters SpawnParameters;
	SpawnParameters.Name = TEXT("M01_P4_Landscape_Production");
	SpawnParameters.SpawnCollisionHandlingOverride =
		ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	ALandscape* Landscape = Director->GetWorld()->SpawnActor<ALandscape>(
		ALandscape::StaticClass(),
		FVector(0.f, 7000.f, -120.f),
		FRotator::ZeroRotator,
		SpawnParameters);
	if (!Landscape)
	{
		Result.Error = TEXT("Could not spawn governed Landscape.");
		return Result;
	}
	Landscape->SetActorLabel(TEXT("M01_P4_Landscape_Production"));
	Landscape->Tags.AddUnique(LandscapeTag);
	Landscape->SetActorRelativeScale3D(FVector(100.f));

	const FGuid LandscapeGuid = FGuid::NewGuid();
	const FGuid BaseLayerGuid;
	TMap<FGuid, TArray<uint16>> HeightDataPerLayer;
	HeightDataPerLayer.Add(BaseLayerGuid, MoveTemp(HeightSamples));
	TMap<FGuid, TArray<FLandscapeImportLayerInfo>> MaterialDataPerLayer;
	// ALandscapeProxy::Import requires one material-layer-info array for every
	// height-data layer, including the empty base/final layer. Supplying no
	// matching entry triggers LandscapeEdit.cpp's fail-fast count assertion
	// before any components can be authored.
	MaterialDataPerLayer.Add(
		BaseLayerGuid,
		TArray<FLandscapeImportLayerInfo>());
	Landscape->Import(
		LandscapeGuid,
		0,
		0,
		HeightmapWidth - 1,
		HeightmapHeight - 1,
		1,
		63,
		HeightDataPerLayer,
		*HeightmapSourcePath,
		MaterialDataPerLayer,
		ELandscapeImportAlphamapType::Additive,
		TArrayView<const FLandscapeLayer>());
	Landscape->CreateLandscapeInfo();
	Landscape->RegisterAllComponents();
	Landscape->PostEditChange();

	TArray<ULandscapeComponent*> LandscapeComponents;
	Landscape->GetComponents<ULandscapeComponent>(LandscapeComponents);
	if (!Landscape->GetLandscapeGuid().IsValid()
		|| LandscapeComponents.Num() != 16)
	{
		Result.Error = FString::Printf(
			TEXT("Landscape import produced guid=%s components=%d; expected 16."),
			*Landscape->GetLandscapeGuid().ToString(),
			LandscapeComponents.Num());
		Landscape->Destroy();
		return Result;
	}

	UPackage* GraphPackage = CreatePackage(*GraphPackagePath);
	const FString GraphAssetName =
		FPackageName::GetLongPackageAssetName(GraphPackagePath);
	UPCGGraph* Graph = NewObject<UPCGGraph>(
		GraphPackage,
		*GraphAssetName,
		RF_Public | RF_Standalone | RF_Transactional);
	if (!Graph)
	{
		Result.Error = TEXT("Could not allocate governed PCG graph.");
		Landscape->Destroy();
		return Result;
	}
	Graph->Description = FText::FromString(
		TEXT("M01 inland vegetation: Landscape sample bounded by explicit ")
		TEXT("inclusion/exclusion components. Licensed mesh slots intentionally ")
		TEXT("empty; generation is authorization-gated."));
	Graph->bLandscapeUsesMetadata = false;

	UPCGGetLandscapeSettings* LandscapeSettings = nullptr;
	UPCGDataFromActorSettings* InclusionSettings = nullptr;
	UPCGSurfaceSamplerSettings* SurfaceSettings = nullptr;
	UPCGDataFromActorSettings* ExclusionSettings = nullptr;
	UPCGDifferenceSettings* DifferenceSettings = nullptr;
	UPCGDensityFilterSettings* DensitySettings = nullptr;
	UPCGTransformPointsSettings* TransformSettings = nullptr;
	UPCGStaticMeshSpawnerSettings* SpawnerSettings = nullptr;

	UPCGNode* LandscapeNode = AddGovernedNode(
		Graph, LandscapeSettings, TEXT("landscape_data"), -1000, -240);
	UPCGNode* InclusionNode = AddGovernedNode(
		Graph, InclusionSettings, TEXT("inclusion_bounds"), -1000, 80);
	UPCGNode* SurfaceNode = AddGovernedNode(
		Graph, SurfaceSettings, TEXT("surface_sample"), -680, -120);
	UPCGNode* ExclusionNode = AddGovernedNode(
		Graph, ExclusionSettings, TEXT("route_and_beach_exclusion"), -680, 220);
	UPCGNode* DifferenceNode = AddGovernedNode(
		Graph, DifferenceSettings, TEXT("route_and_beach_difference"), -360, -40);
	UPCGNode* DensityNode = AddGovernedNode(
		Graph, DensitySettings, TEXT("density_filter"), -40, -40);
	UPCGNode* TransformNode = AddGovernedNode(
		Graph, TransformSettings, TEXT("deterministic_transform"), 280, -40);
	UPCGNode* SpawnerNode = AddGovernedNode(
		Graph, SpawnerSettings, TEXT("governed_mesh_spawn"), 600, -40);

	const bool bNodesValid =
		LandscapeNode && InclusionNode && SurfaceNode && ExclusionNode
		&& DifferenceNode && DensityNode && TransformNode && SpawnerNode
		&& LandscapeSettings && InclusionSettings && SurfaceSettings
		&& ExclusionSettings && DifferenceSettings && DensitySettings
		&& TransformSettings && SpawnerSettings;
	if (!bNodesValid)
	{
		Result.Error = TEXT("Could not allocate the governed PCG node set.");
		Landscape->Destroy();
		Graph->ClearFlags(RF_Public | RF_Standalone);
		return Result;
	}

	LandscapeSettings->Seed = 5201;
	ConfigureSelfComponentSelector(InclusionSettings, InclusionTag, 5201);
	ConfigureSelfComponentSelector(ExclusionSettings, ExclusionTag, 5201);
	SurfaceSettings->Seed = 5201;
	SurfaceSettings->PointsPerSquaredMeter = 0.0125f;
	SurfaceSettings->PointExtents = FVector(200.f, 200.f, 100.f);
	SurfaceSettings->Looseness = 0.75f;
	SurfaceSettings->bUnbounded = false;
	DifferenceSettings->Seed = 5201;
	DifferenceSettings->Mode = EPCGDifferenceMode::Discrete;
	DifferenceSettings->DensityFunction =
		EPCGDifferenceDensityFunction::Minimum;
	DensitySettings->Seed = 5201;
	DensitySettings->LowerBound = 0.15f;
	DensitySettings->UpperBound = 1.f;
	TransformSettings->Seed = 5201;
	TransformSettings->RotationMin = FRotator(0.f, -180.f, 0.f);
	TransformSettings->RotationMax = FRotator(0.f, 180.f, 0.f);
	TransformSettings->ScaleMin = FVector(0.85f);
	TransformSettings->ScaleMax = FVector(1.2f);
	TransformSettings->bUniformScale = true;
	TransformSettings->bRecomputeSeed = true;
	SpawnerSettings->Seed = 5201;
	SpawnerSettings->SetMeshSelectorType(
		UPCGMeshSelectorWeighted::StaticClass());
	UPCGMeshSelectorWeighted* WeightedSelector =
		Cast<UPCGMeshSelectorWeighted>(
			SpawnerSettings->MeshSelectorParameters);
	if (!WeightedSelector)
	{
		Result.Error = TEXT("Could not configure empty governed mesh selector.");
		Landscape->Destroy();
		Graph->ClearFlags(RF_Public | RF_Standalone);
		return Result;
	}
	WeightedSelector->MeshEntries.Reset();

	Graph->AddEdge(
		LandscapeNode,
		PCGPinConstants::DefaultOutputLabel,
		SurfaceNode,
		PCGSurfaceSamplerConstants::SurfaceLabel);
	Graph->AddEdge(
		InclusionNode,
		PCGPinConstants::DefaultOutputLabel,
		SurfaceNode,
		PCGSurfaceSamplerConstants::BoundingShapeLabel);
	Graph->AddEdge(
		SurfaceNode,
		PCGPinConstants::DefaultOutputLabel,
		DifferenceNode,
		PCGDifferenceConstants::SourceLabel);
	Graph->AddEdge(
		ExclusionNode,
		PCGPinConstants::DefaultOutputLabel,
		DifferenceNode,
		PCGDifferenceConstants::DifferencesLabel);
	Graph->AddEdge(
		DifferenceNode,
		PCGPinConstants::DefaultOutputLabel,
		DensityNode,
		PCGPinConstants::DefaultInputLabel);
	Graph->AddEdge(
		DensityNode,
		PCGPinConstants::DefaultOutputLabel,
		TransformNode,
		PCGPinConstants::DefaultInputLabel);
	Graph->AddEdge(
		TransformNode,
		PCGPinConstants::DefaultOutputLabel,
		SpawnerNode,
		PCGPinConstants::DefaultInputLabel);
	Graph->AddEdge(
		SpawnerNode,
		PCGPinConstants::DefaultOutputLabel,
		Graph->GetOutputNode(),
		// PCG graph output nodes expose their receiving pin under the
		// graph-output label ("Out"), not the ordinary element input label
		// ("In"). This mirrors the engine's own subgraph construction tests.
		PCGPinConstants::DefaultOutputLabel);

	if (Graph->GetNodes().Num() != 8
		|| Graph->GetAllEdges().Num() != 8)
	{
		Result.Error = FString::Printf(
			TEXT("Graph topology nodes=%d edges=%d; expected 8/8."),
			Graph->GetNodes().Num(),
			Graph->GetAllEdges().Num());
		Landscape->Destroy();
		Graph->ClearFlags(RF_Public | RF_Standalone);
		return Result;
	}

	FAssetRegistryModule& AssetRegistry =
		FModuleManager::LoadModuleChecked<FAssetRegistryModule>(
			TEXT("AssetRegistry"));
	AssetRegistry.AssetCreated(Graph);
	GraphPackage->MarkPackageDirty();

	Director->ProductionLandscape = Landscape;
	Director->AuthoredPCGGraph = Graph;
	Director->bLicensedVegetationLibraryApproved = false;
	Director->bAllowAuthoredPCGGeneration = false;
	Director->RefreshAuthoredEnvironmentBindings();

	Result = AuditGovernedLandscapeAndGraph(Director);
	if (!Result.bSuccess && Result.Error.IsEmpty())
	{
		Result.Error =
			TEXT("Serialized handoff did not reach safe structural readiness.");
	}
	return Result;
#endif
}

FSkyguardMission01EnvironmentAuthoringResult
USkyguardMission01EnvironmentAuthoringLibrary::
AuthorGovernedLandscapeWithExistingGraph(
	ASkyguardMission01EnvironmentDirector* Director,
	const FString& HeightmapSourcePath,
	const FString& GraphPackagePath)
{
	FSkyguardMission01EnvironmentAuthoringResult Result;

#if !WITH_EDITOR
	Result.Error = TEXT("The governed authoring bridge is editor-only.");
	return Result;
#else
	if (!Director || !Director->GetWorld())
	{
		Result.Error = TEXT("A director in a valid editor world is required.");
		return Result;
	}
	if (!FPackageName::IsValidLongPackageName(GraphPackagePath)
		|| !FPackageName::DoesPackageExist(GraphPackagePath))
	{
		Result.Error = FString::Printf(
			TEXT("Accepted graph package is unavailable: %s"),
			*GraphPackagePath);
		return Result;
	}

	const FString GraphObjectPath =
		GraphPackagePath + TEXT(".")
		+ FPackageName::GetLongPackageAssetName(GraphPackagePath);
	UPCGGraph* Graph = LoadObject<UPCGGraph>(
		nullptr,
		*GraphObjectPath);
	if (!Graph)
	{
		Result.Error = FString::Printf(
			TEXT("Could not load accepted graph without mutation: %s"),
			*GraphObjectPath);
		return Result;
	}

	TArray<uint8> HeightBytes;
	if (!FFileHelper::LoadFileToArray(HeightBytes, *HeightmapSourcePath))
	{
		Result.Error = FString::Printf(
			TEXT("Could not load governed height source: %s"),
			*HeightmapSourcePath);
		return Result;
	}
	if (HeightBytes.Num() != ExpectedHeightmapBytes)
	{
		Result.Error = FString::Printf(
			TEXT("Height source bytes=%d; expected=%d."),
			HeightBytes.Num(),
			ExpectedHeightmapBytes);
		return Result;
	}

	for (TActorIterator<ALandscape> It(Director->GetWorld()); It; ++It)
	{
		if (It->ActorHasTag(LandscapeTag)
			|| It->GetActorLabel()
				== TEXT("M01_P4_Landscape_Production"))
		{
			Result.Error =
				TEXT("Immutable candidate world already contains governed Landscape.");
			return Result;
		}
	}

	TArray<uint16> HeightSamples;
	HeightSamples.SetNumUninitialized(HeightmapWidth * HeightmapHeight);
	for (int32 Index = 0; Index < HeightSamples.Num(); ++Index)
	{
		const int32 ByteIndex = Index * 2;
		HeightSamples[Index] =
			static_cast<uint16>(HeightBytes[ByteIndex])
			| (static_cast<uint16>(HeightBytes[ByteIndex + 1]) << 8);
	}

	FActorSpawnParameters SpawnParameters;
	SpawnParameters.Name = TEXT("M01_P4_Landscape_Production");
	SpawnParameters.SpawnCollisionHandlingOverride =
		ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	ALandscape* Landscape = Director->GetWorld()->SpawnActor<ALandscape>(
		ALandscape::StaticClass(),
		FVector(0.f, 7000.f, -120.f),
		FRotator::ZeroRotator,
		SpawnParameters);
	if (!Landscape)
	{
		Result.Error = TEXT("Could not spawn governed Landscape.");
		return Result;
	}
	Landscape->SetActorLabel(TEXT("M01_P4_Landscape_Production"));
	Landscape->Tags.AddUnique(LandscapeTag);
	Landscape->SetActorRelativeScale3D(FVector(100.f));

	const FGuid LandscapeGuid = FGuid::NewGuid();
	const FGuid BaseLayerGuid;
	TMap<FGuid, TArray<uint16>> HeightDataPerLayer;
	HeightDataPerLayer.Add(BaseLayerGuid, MoveTemp(HeightSamples));
	TMap<FGuid, TArray<FLandscapeImportLayerInfo>> MaterialDataPerLayer;
	MaterialDataPerLayer.Add(
		BaseLayerGuid,
		TArray<FLandscapeImportLayerInfo>());
	Landscape->Import(
		LandscapeGuid,
		0,
		0,
		HeightmapWidth - 1,
		HeightmapHeight - 1,
		1,
		63,
		HeightDataPerLayer,
		*HeightmapSourcePath,
		MaterialDataPerLayer,
		ELandscapeImportAlphamapType::Additive,
		TArrayView<const FLandscapeLayer>());
	Landscape->CreateLandscapeInfo();
	Landscape->RegisterAllComponents();
	Landscape->PostEditChange();

	TArray<ULandscapeComponent*> LandscapeComponents;
	Landscape->GetComponents<ULandscapeComponent>(LandscapeComponents);
	if (!Landscape->GetLandscapeGuid().IsValid()
		|| LandscapeComponents.Num() != 16)
	{
		Result.Error = FString::Printf(
			TEXT("Landscape import produced guid=%s components=%d; expected 16."),
			*Landscape->GetLandscapeGuid().ToString(),
			LandscapeComponents.Num());
		Landscape->Destroy();
		return Result;
	}

	Director->ProductionLandscape = Landscape;
	Director->AuthoredPCGGraph = Graph;
	Director->bLicensedVegetationLibraryApproved = false;
	Director->bAllowAuthoredPCGGeneration = false;
	Director->RefreshAuthoredEnvironmentBindings();

	Result = AuditGovernedLandscapeAndGraph(Director);
	if (!Result.bSuccess && Result.Error.IsEmpty())
	{
		Result.Error =
			TEXT("Candidate handoff did not reach safe structural readiness.");
	}
	return Result;
#endif
}

FSkyguardMission01EnvironmentAuthoringResult
USkyguardMission01EnvironmentAuthoringLibrary::
AuditGovernedLandscapeAndGraph(
	ASkyguardMission01EnvironmentDirector* Director)
{
	FSkyguardMission01EnvironmentAuthoringResult Result;

#if !WITH_EDITOR
	Result.Error = TEXT("The governed authoring audit is editor-only.");
	return Result;
#else
	if (!Director || !Director->GetWorld())
	{
		Result.Error = TEXT("A director in a valid editor world is required.");
		return Result;
	}

	Director->RefreshAuthoredEnvironmentBindings();
	ALandscape* Landscape = Cast<ALandscape>(
		Director->ProductionLandscape.Get());
	UPCGGraph* Graph = Cast<UPCGGraph>(
		Director->AuthoredPCGGraph.LoadSynchronous());
	Result.Landscape = Landscape;
	Result.Graph = Graph;
	if (!Landscape || !Graph)
	{
		Result.Error =
			TEXT("The governed Landscape or graph binding is missing.");
		return Result;
	}

	TArray<ULandscapeComponent*> LandscapeComponents;
	Landscape->GetComponents<ULandscapeComponent>(LandscapeComponents);
	Result.LandscapeComponentCount = LandscapeComponents.Num();
	Result.bLandscapeGuidValid =
		Landscape->GetLandscapeGuid().IsValid();
	const FVector Location = Landscape->GetActorLocation();
	const FVector Scale = Landscape->GetActorScale3D();
	Result.bLandscapeTransformExact =
		Location.Equals(FVector(0.f, 7000.f, -120.f), 0.01f)
		&& Scale.Equals(FVector(100.f), 0.01f);

	TMap<FString, int32> NodeCounts;
	for (const UPCGNode* Node : Graph->GetNodes())
	{
		const UPCGSettings* Settings = Node ? Node->GetSettings() : nullptr;
		if (!Settings)
		{
			continue;
		}
		const FString ClassName =
			TEXT("U") + Settings->GetClass()->GetName();
		Result.GraphNodeSettingClasses.Add(ClassName);
		NodeCounts.FindOrAdd(ClassName) += 1;
	}
	Result.GraphNodeSettingClasses.Sort();
	Result.GraphNodeCount = Graph->GetNodes().Num();
	Result.GraphEdgeCount = Graph->GetAllEdges().Num();
	const TMap<FString, int32> RequiredCounts = {
		{TEXT("UPCGGetLandscapeSettings"), 1},
		{TEXT("UPCGDataFromActorSettings"), 2},
		{TEXT("UPCGSurfaceSamplerSettings"), 1},
		{TEXT("UPCGDifferenceSettings"), 1},
		{TEXT("UPCGDensityFilterSettings"), 1},
		{TEXT("UPCGTransformPointsSettings"), 1},
		{TEXT("UPCGStaticMeshSpawnerSettings"), 1},
	};
	Result.bGraphContractValid =
		Result.GraphNodeCount == 8
		&& Result.GraphEdgeCount == 8;
	for (const TPair<FString, int32>& Required : RequiredCounts)
	{
		Result.bGraphContractValid &=
			NodeCounts.FindRef(Required.Key) == Required.Value;
	}

	Result.bLicensedMeshSlotsEmpty = false;
	for (const UPCGNode* Node : Graph->GetNodes())
	{
		const UPCGStaticMeshSpawnerSettings* Spawner =
			Node
			? Cast<UPCGStaticMeshSpawnerSettings>(Node->GetSettings())
			: nullptr;
		if (!Spawner)
		{
			continue;
		}
		const UPCGMeshSelectorWeighted* Weighted =
			Cast<UPCGMeshSelectorWeighted>(
				Spawner->MeshSelectorParameters);
		Result.bLicensedMeshSlotsEmpty =
			Weighted && Weighted->MeshEntries.IsEmpty();
		break;
	}

	const FName GeneratedComponentTag =
		TEXT("PCG Generated Component");
	for (TActorIterator<AActor> ActorIt(Director->GetWorld());
		ActorIt;
		++ActorIt)
	{
		TInlineComponentArray<UActorComponent*> Components;
		ActorIt->GetComponents(Components);
		for (const UActorComponent* Component : Components)
		{
			if (!Component
				|| !Component->ComponentHasTag(GeneratedComponentTag))
			{
				continue;
			}
			++Result.GeneratedPCGComponentCount;
			if (const UInstancedStaticMeshComponent* ISM =
				Cast<UInstancedStaticMeshComponent>(Component))
			{
				Result.GeneratedPCGInstanceCount +=
					ISM->GetInstanceCount();
			}
		}
	}
	Result.bRouteAndBeachGeneratedInstancesZero =
		Result.GeneratedPCGComponentCount == 0
		&& Result.GeneratedPCGInstanceCount == 0;
	Result.bAuthoredStructureReady =
		Director->GetReadiness().bAuthoredPCGStructureReady;
	Result.bGenerationLocked =
		!Director->IsPCGGenerationAuthorized()
		&& Director->InlandVegetationPCG
		&& !Director->InlandVegetationPCG->bActivated;
	Result.bSuccess =
		Result.LandscapeComponentCount == 16
		&& Result.bLandscapeGuidValid
		&& Result.bLandscapeTransformExact
		&& Result.bGraphContractValid
		&& Result.bAuthoredStructureReady
		&& Result.bLicensedMeshSlotsEmpty
		&& Result.bGenerationLocked
		&& Result.bRouteAndBeachGeneratedInstancesZero;
	Result.VisibleAudit = AuditLandscapeVisibleReadiness(
		Landscape,
		Landscape->GetLandscapeMaterial());
	if (!Result.bSuccess)
	{
		Result.Error =
			TEXT("Governed Landscape/PCG audit did not satisfy all structural and generation-lock checks.");
	}
	return Result;
#endif
}

FSkyguardLandscapeVisibleAudit
USkyguardMission01EnvironmentAuthoringLibrary::
PrepareGovernedLandscapeForVisibleValidation(
	ALandscape* Landscape,
	UMaterialInterface* GovernedMaterial)
{
	FSkyguardLandscapeVisibleAudit Result;
#if !WITH_EDITOR
	Result.Error = TEXT("Landscape visible preparation is editor-only.");
	return Result;
#else
	if (!Landscape || !GovernedMaterial)
	{
		Result.Error = TEXT("Landscape and governed material are required.");
		return Result;
	}

	Landscape->SetActorHiddenInGame(false);
	Landscape->SetIsTemporarilyHiddenInEditor(false);
	Landscape->LandscapeMaterial = GovernedMaterial;

	TArray<ULandscapeComponent*> Components;
	Landscape->GetComponents<ULandscapeComponent>(Components);
	for (ULandscapeComponent* Component : Components)
	{
		if (!Component)
		{
			continue;
		}
		Component->SetVisibility(true, true);
		Component->SetHiddenInGame(false, true);
		if (!Component->IsRegistered())
		{
			Component->RegisterComponent();
		}
		Component->UpdateCachedBounds(false);
	}
	Landscape->UpdateAllComponentMaterialInstances(true);
	for (ULandscapeComponent* Component : Components)
	{
		if (!Component)
		{
			continue;
		}
		if (Component->IsRegistered())
		{
			Component->RecreateRenderState_Concurrent();
		}
		Component->MarkRenderStateDirty();
	}
	Landscape->MarkComponentsRenderStateDirty();
	return AuditLandscapeVisibleReadiness(Landscape, GovernedMaterial);
#endif
}

FSkyguardLandscapeVisibleAudit
USkyguardMission01EnvironmentAuthoringLibrary::
AuditLandscapeVisibleReadiness(
	ALandscape* Landscape,
	UMaterialInterface* GovernedMaterial)
{
	FSkyguardLandscapeVisibleAudit Result;
#if !WITH_EDITOR
	Result.Error = TEXT("Landscape visible audit is editor-only.");
	return Result;
#else
	if (!Landscape || !GovernedMaterial)
	{
		Result.Error = TEXT("Landscape and governed material are required.");
		return Result;
	}

	Result.bActorHiddenInGame = Landscape->IsHidden();
	Result.bActorTemporarilyHiddenInEditor =
		Landscape->IsTemporarilyHiddenInEditor();
	TArray<ULandscapeComponent*> Components;
	Landscape->GetComponents<ULandscapeComponent>(Components);
	Result.LandscapeComponentCount = Components.Num();
	FBox CombinedBounds(ForceInit);
	for (ULandscapeComponent* Component : Components)
	{
		if (!Component)
		{
			continue;
		}
		Result.VisibleComponentCount += Component->GetVisibleFlag() ? 1 : 0;
		Result.RegisteredComponentCount += Component->IsRegistered() ? 1 : 0;
		Result.RenderStateCreatedComponentCount +=
			Component->IsRenderStateCreated() ? 1 : 0;
		Result.HiddenInGameComponentCount +=
			Component->bHiddenInGame ? 1 : 0;
		CombinedBounds += Component->Bounds.GetBox();

		UMaterialInstance* GeneratedInstance = nullptr;
		if (Component->GetMaterialInstanceCount(false) > 0)
		{
			GeneratedInstance = Component->GetMaterialInstance(0, false);
		}
		if (GeneratedInstance)
		{
			++Result.GeneratedMaterialInstanceReadyComponentCount;
			if (GeneratedInstance->IsChildOf(GovernedMaterial)
				|| GeneratedInstance->GetMaterial()
					== GovernedMaterial->GetMaterial())
			{
				++Result.GovernedMaterialParentMatchComponentCount;
			}
		}
	}

	Result.bBoundsFiniteAndNonzero =
		CombinedBounds.IsValid
		&& CombinedBounds.GetSize().GetMin() > UE_KINDA_SMALL_NUMBER
		&& !CombinedBounds.Min.ContainsNaN()
		&& !CombinedBounds.Max.ContainsNaN();
	if (CombinedBounds.IsValid)
	{
		Result.BoundsMinimum = CombinedBounds.Min;
		Result.BoundsMaximum = CombinedBounds.Max;
		for (const FContractCamera& Camera : ContractCameras)
		{
			Result.ContractCameraFrustumIntersectionCount +=
				DoesBoundsIntersectContractCamera(CombinedBounds, Camera)
				? 1
				: 0;
		}
	}

	Result.bSuccess =
		Result.LandscapeComponentCount == 16
		&& Result.VisibleComponentCount == 16
		&& Result.RegisteredComponentCount == 16
		&& Result.RenderStateCreatedComponentCount == 16
		&& Result.HiddenInGameComponentCount == 0
		&& Result.GeneratedMaterialInstanceReadyComponentCount == 16
		&& Result.GovernedMaterialParentMatchComponentCount == 16
		&& Result.ContractCameraFrustumIntersectionCount == 5
		&& !Result.bActorHiddenInGame
		&& !Result.bActorTemporarilyHiddenInEditor
		&& Result.bBoundsFiniteAndNonzero;
	if (!Result.bSuccess)
	{
		Result.Error =
			TEXT("Landscape live render-readiness audit did not satisfy ")
			TEXT("the governed 16-component and five-camera contract.");
	}
	return Result;
#endif
}

FSkyguardLandscapeCaptureConfigurationResult
USkyguardMission01EnvironmentAuthoringLibrary::
ConfigureLandscapeSceneCaptureDiagnostic(
	USceneCaptureComponent2D* Capture,
	ALandscape* Landscape,
	const ESkyguardLandscapeCaptureDiagnosticMode Mode)
{
	FSkyguardLandscapeCaptureConfigurationResult Result;
	Result.Mode = Mode;
	if (!Capture)
	{
		Result.Error = TEXT("SceneCaptureComponent2D is required.");
		return Result;
	}
	if ((Mode == ESkyguardLandscapeCaptureDiagnosticMode::LandscapeCoverage
			|| Mode
				== ESkyguardLandscapeCaptureDiagnosticMode::ComponentBoundary)
		&& !Landscape)
	{
		Result.Error =
			TEXT("Landscape is required for show-only diagnostic modes.");
		return Result;
	}

	Capture->ClearHiddenComponents();
	Capture->ClearShowOnlyComponents();
	Capture->bCaptureEveryFrame = false;
	Capture->bCaptureOnMovement = false;
	Capture->CaptureSource = SCS_FinalColorLDR;
	FEngineShowFlags Flags(ESFIM_Game);
	if (Mode == ESkyguardLandscapeCaptureDiagnosticMode::ShaderComplexity)
	{
		ApplyViewMode(VMI_ShaderComplexity, true, Flags);
		Result.ViewMode = TEXT("VMI_ShaderComplexity");
		Capture->PrimitiveRenderMode =
			ESceneCapturePrimitiveRenderMode::PRM_RenderScenePrimitives;
	}
	else
	{
		ApplyViewMode(VMI_Lit, true, Flags);
		Result.ViewMode = TEXT("VMI_Lit");
		if (Mode
				== ESkyguardLandscapeCaptureDiagnosticMode::LandscapeCoverage
			|| Mode
				== ESkyguardLandscapeCaptureDiagnosticMode::ComponentBoundary)
		{
			// Preserve the diagnostic material's exact linear palette. The
			// offline verifier decodes RGB8 to linear before matching IDs.
			Flags.SetTonemapper(false);
			Flags.SetPostProcessing(false);
			Flags.SetAtmosphere(false);
			Flags.SetDeferredAtmospherePass(false);
			Flags.SetCloud(false);
			Flags.SetFog(false);
			Flags.SetVolumetricFog(false);
			Flags.SetSkyLighting(false);
			TArray<ULandscapeComponent*> Components;
			Landscape->GetComponents<ULandscapeComponent>(Components);
			if (Components.Num() != 16)
			{
				Result.Error = FString::Printf(
					TEXT("Expected exactly 16 Landscape components; found %d."),
					Components.Num());
				return Result;
			}
			Capture->PrimitiveRenderMode =
				ESceneCapturePrimitiveRenderMode::PRM_UseShowOnlyList;
			UMaterialInterface* DiagnosticMaterial =
				Landscape->LandscapeMaterial;
			for (ULandscapeComponent* Component : Components)
			{
				if (!Component
					|| !Component->IsRegistered()
					|| !Component->IsRenderStateCreated()
					|| !Component->GetVisibleFlag()
					|| Component->bHiddenInGame)
				{
					Result.Error =
						TEXT("A Landscape component is not capture-ready.");
					return Result;
				}
				UMaterialInstance* GeneratedInstance = nullptr;
				if (Component->GetMaterialInstanceCount(false) > 0)
				{
					GeneratedInstance =
						Component->GetMaterialInstance(0, false);
				}
				if (GeneratedInstance)
				{
					++Result.GeneratedMaterialInstanceReadyComponentCount;
					if (DiagnosticMaterial
						&& (GeneratedInstance->IsChildOf(DiagnosticMaterial)
							|| GeneratedInstance->GetMaterial()
								== DiagnosticMaterial->GetMaterial()))
					{
						++Result.DiagnosticMaterialParentMatchComponentCount;
					}
				}
				Capture->ShowOnlyComponent(Component);
				++Result.ShowOnlyLandscapeComponentCount;
			}
			if (Result.ShowOnlyLandscapeComponentCount != 16
				|| Result.GeneratedMaterialInstanceReadyComponentCount != 16
				|| Result.DiagnosticMaterialParentMatchComponentCount != 16)
			{
				Result.Error =
					TEXT("Explicit 16-component show-only/material audit failed.");
				return Result;
			}
			Result.bUsesShowOnlyLandscape = true;
		}
		else
		{
			Capture->PrimitiveRenderMode =
				ESceneCapturePrimitiveRenderMode::PRM_RenderScenePrimitives;
		}
	}
	PRAGMA_DISABLE_DEPRECATION_WARNINGS
	Capture->ShowFlags = Flags;
	PRAGMA_ENABLE_DEPRECATION_WARNINGS
	Capture->MarkRenderStateDirty();
	FlushRenderingCommands();
	Result.bRenderThreadSynchronized = true;
	Result.CaptureSource = TEXT("SCS_FinalColorLDR");
	Result.bSuccess = true;
	return Result;
}

namespace
{
	FSkyguardLandscapeMaterialCompilationResult
	AuditLandscapeMaterialCompilationInternal(
		ALandscape* Landscape,
		UMaterialInterface* ExpectedParentMaterial,
		const bool bFinishCompilation)
	{
		FSkyguardLandscapeMaterialCompilationResult Result;
#if !WITH_EDITOR
		Result.Error =
			TEXT("Landscape material compilation audit is editor-only.");
		return Result;
#else
		if (!Landscape || !ExpectedParentMaterial || !Landscape->GetWorld())
		{
			Result.Error =
				TEXT("Landscape, material, and editor world are required.");
			return Result;
		}
		if (!IsInGameThread())
		{
			Result.Error =
				TEXT("Landscape material compilation audit requires the game thread.");
			return Result;
		}
		if (bFinishCompilation)
		{
			FAssetCompilingManager::Get().FinishAllCompilation();
			if (GShaderCompilingManager)
			{
				GShaderCompilingManager->FinishAllCompilation();
			}
		}

		const EShaderPlatform ShaderPlatform =
			GetFeatureLevelShaderPlatform_Checked(
				Landscape->GetWorld()->GetFeatureLevel());
		TArray<ULandscapeComponent*> Components;
		Landscape->GetComponents<ULandscapeComponent>(Components);
		Result.LandscapeComponentCount = Components.Num();
		for (ULandscapeComponent* Component : Components)
		{
			if (!Component
				|| Component->GetMaterialInstanceCount(false) <= 0)
			{
				continue;
			}
			UMaterialInstance* GeneratedInstance =
				Component->GetMaterialInstance(0, false);
			if (!GeneratedInstance
				|| (!GeneratedInstance->IsChildOf(ExpectedParentMaterial)
					&& GeneratedInstance->GetMaterial()
						!= ExpectedParentMaterial->GetMaterial()))
			{
				continue;
			}
			++Result.GeneratedMaterialInstanceCount;
			FMaterialResource* Resource =
				GeneratedInstance->GetMaterialResource(ShaderPlatform);
			if (!Resource)
			{
				continue;
			}
			++Result.MaterialResourceCount;
			if (bFinishCompilation)
			{
				Resource->FinishCompilation();
			}
			if (Resource->IsCompilationFinished())
			{
				++Result.CompilationFinishedResourceCount;
			}
			FMaterialShaderMap* ShaderMap =
				Resource->GetGameThreadShaderMap();
			if (ShaderMap && ShaderMap->IsValidForRendering())
			{
				++Result.ValidShaderMapResourceCount;
			}
		}
		Result.bAssetCompilationQueueEmpty =
			FAssetCompilingManager::Get().GetNumRemainingAssets() == 0;
		Result.bShaderCompilationQueueEmpty =
			!GShaderCompilingManager
			|| !GShaderCompilingManager->IsCompiling();
		Result.bSuccess =
			Result.LandscapeComponentCount == 16
			&& Result.GeneratedMaterialInstanceCount == 16
			&& Result.MaterialResourceCount == 16
			&& Result.CompilationFinishedResourceCount == 16
			&& Result.ValidShaderMapResourceCount == 16
			&& Result.bAssetCompilationQueueEmpty
			&& Result.bShaderCompilationQueueEmpty;
		if (!Result.bSuccess)
		{
			Result.Error =
				TEXT("Generated Landscape material resources are not fully compiled ")
				TEXT("and valid for rendering across all 16 components.");
		}
		return Result;
#endif
	}
}

FSkyguardLandscapeMaterialCompilationResult
USkyguardMission01EnvironmentAuthoringLibrary::
FinishLandscapeMaterialCompilation(
	ALandscape* Landscape,
	UMaterialInterface* ExpectedParentMaterial)
{
	return AuditLandscapeMaterialCompilationInternal(
		Landscape,
		ExpectedParentMaterial,
		true);
}

FSkyguardLandscapeMaterialCompilationResult
USkyguardMission01EnvironmentAuthoringLibrary::
AuditLandscapeMaterialCompilation(
	ALandscape* Landscape,
	UMaterialInterface* ExpectedParentMaterial)
{
	return AuditLandscapeMaterialCompilationInternal(
		Landscape,
		ExpectedParentMaterial,
		false);
}

FSkyguardLandscapeVisibleAudit
USkyguardMission01EnvironmentAuthoringLibrary::
BeginTransientLandscapeDiagnosticMaterialDeferred(
	ALandscape* Landscape,
	UMaterialInterface* Material)
{
	FSkyguardLandscapeVisibleAudit Result;
#if !WITH_EDITOR
	Result.Error =
		TEXT("Deferred Landscape diagnostic material override is editor-only.");
	return Result;
#else
	if (!Landscape || !Material)
	{
		Result.Error = TEXT("Landscape and diagnostic material are required.");
		return Result;
	}
	Landscape->LandscapeMaterial = Material;
	Landscape->UpdateAllComponentMaterialInstances(true);
	TArray<ULandscapeComponent*> Components;
	Landscape->GetComponents<ULandscapeComponent>(Components);
	for (ULandscapeComponent* Component : Components)
	{
		if (!Component)
		{
			continue;
		}
		Component->UpdateCachedBounds(false);
		if (Component->IsRegistered())
		{
			Component->RecreateRenderState_Concurrent();
		}
		Component->MarkRenderStateDirty();
	}
	Landscape->MarkComponentsRenderStateDirty();
	FlushRenderingCommands();
	return AuditLandscapeVisibleReadiness(Landscape, Material);
#endif
}

bool USkyguardMission01EnvironmentAuthoringLibrary::
SetTransientLandscapeDiagnosticMaterial(
	ALandscape* Landscape,
	UMaterialInterface* Material)
{
	return SetTransientLandscapeDiagnosticMaterialSynchronized(
		Landscape,
		Material).bSuccess;
}

FSkyguardLandscapeVisibleAudit
USkyguardMission01EnvironmentAuthoringLibrary::
SetTransientLandscapeDiagnosticMaterialSynchronized(
	ALandscape* Landscape,
	UMaterialInterface* Material)
{
	FSkyguardLandscapeVisibleAudit Result;
#if !WITH_EDITOR
	Result.Error = TEXT("Landscape diagnostic material override is editor-only.");
	return Result;
#else
	if (!Landscape || !Material)
	{
		Result.Error = TEXT("Landscape and diagnostic material are required.");
		return Result;
	}
	Landscape->LandscapeMaterial = Material;
	Landscape->UpdateAllComponentMaterialInstances(true);
	const FSkyguardLandscapeMaterialCompilationResult Compilation =
		FinishLandscapeMaterialCompilation(Landscape, Material);
	if (!Compilation.bSuccess)
	{
		Result.Error = Compilation.Error;
		return Result;
	}
	TArray<ULandscapeComponent*> Components;
	Landscape->GetComponents<ULandscapeComponent>(Components);
	for (ULandscapeComponent* Component : Components)
	{
		if (!Component)
		{
			continue;
		}
		Component->UpdateCachedBounds(false);
		if (Component->IsRegistered())
		{
			Component->RecreateRenderState_Concurrent();
		}
		Component->MarkRenderStateDirty();
	}
	Landscape->MarkComponentsRenderStateDirty();
	FlushRenderingCommands();
	return AuditLandscapeVisibleReadiness(Landscape, Material);
#endif
}
