using UnrealBuildTool;

public sealed class SkyguardRecovery03NativeRecovery05 : ModuleRules
{
    public SkyguardRecovery03NativeRecovery05(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PrivateDependencyModuleNames.AddRange(
            new[]
            {
                "Core",
                "CoreUObject",
                "Engine",
                "Json",
                "Landscape",
                "Projects",
                "RHI",
                "RenderCore",
                "UnrealEd"
            });
    }
}
