using UnrealBuildTool;

public class HelloGuestTarget : TargetRules
{
	public HelloGuestTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Game;
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		ExtraModuleNames.Add("HelloGuest");
	}
}
