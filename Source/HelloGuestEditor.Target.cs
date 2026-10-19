using UnrealBuildTool;

public class HelloGuestEditorTarget : TargetRules
{
	public HelloGuestEditorTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Editor;
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		ExtraModuleNames.Add("HelloGuest");
	}
}
