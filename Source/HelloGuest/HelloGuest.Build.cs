using UnrealBuildTool;

public class HelloGuest : ModuleRules
{
	public HelloGuest(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicIncludePaths.Add(ModuleDirectory);

		PublicDependencyModuleNames.AddRange(new string[]
		{
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput",
			"AIModule",
			"NavigationSystem",
			"GameplayTasks",
			"DeveloperSettings",
			"EngineSettings",
			"Slate",
			"SlateCore",
			"UMG"
		});
	}
}
