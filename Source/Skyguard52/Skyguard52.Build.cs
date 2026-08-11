using System.IO;
using UnrealBuildTool;

public class Skyguard52 : ModuleRules
{
	public Skyguard52(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
		PublicDependencyModuleNames.AddRange(new string[] {
			"Core", "CoreUObject", "Engine", "InputCore", "EnhancedInput", "UMG",
			"Niagara", "PhysicsCore", "Landscape", "PCG", "EngineCameras"
		});
		PrivateDependencyModuleNames.AddRange(new string[] { "Json", "RenderCore", "RHI" });
		if (Target.bBuildEditor)
		{
			PrivateDependencyModuleNames.AddRange(new string[] {
				"UnrealEd", "AssetRegistry"
			});
		}
		// UE 5.8's stable-cache translation path currently rejects/crashes on the
		// project's otherwise valid captured PSOs. Stage the independently merged
		// runtime cache from Build so the cooker cannot delete it. DefaultGame.ini
		// remaps this directory to Content/PipelineCaches/Windows in the package.
		RuntimeDependencies.Add(
			"$(ProjectDir)/Build/Windows/PipelineCaches/Skyguard52_PCD3D_SM6.stable.upipelinecache",
			StagedFileType.NonUFS
		);
	}
}
