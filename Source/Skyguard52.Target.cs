using UnrealBuildTool;
using System.Collections.Generic;

public class Skyguard52Target : TargetRules
{
	public Skyguard52Target(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Game;
		DefaultBuildSettings = BuildSettingsVersion.V7;
		IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_8;
		ExtraModuleNames.Add("Skyguard52");
	}
}
