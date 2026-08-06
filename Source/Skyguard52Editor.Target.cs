using UnrealBuildTool;
using System.Collections.Generic;

public class Skyguard52EditorTarget : TargetRules
{
	public Skyguard52EditorTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Editor;
		DefaultBuildSettings = BuildSettingsVersion.V7;
		IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_8;
		// Prefer Shared with installed engine; Unique often fails.
		BuildEnvironment = TargetBuildEnvironment.Shared;
		ExtraModuleNames.Add("Skyguard52");
	}
}
