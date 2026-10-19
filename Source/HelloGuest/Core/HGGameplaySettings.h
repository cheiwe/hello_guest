#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "Core/HGTypes.h"
#include "HGGameplaySettings.generated.h"

class USoundBase;
class USkeletalMesh;
class UAnimSequence;

/**
 * All tuning values of the game. Edited in Project Settings > Game > Hello Guest
 * and stored in Config/DefaultGame.ini, so they can be changed without recompiling.
 */
UCLASS(Config = Game, DefaultConfig, meta = (DisplayName = "Hello Guest"))
class HELLOGUEST_API UHGGameplaySettings : public UDeveloperSettings
{
	GENERATED_BODY()

public:
	static const UHGGameplaySettings* Get() { return GetDefault<UHGGameplaySettings>(); }

	virtual FName GetCategoryName() const override { return TEXT("Game"); }

	// --- Player -------------------------------------------------------------

	UPROPERTY(Config, EditAnywhere, Category = "Player", meta = (Units = "cm"))
	float PlayerHeight = 170.f;

	/** Falls higher than this many player heights stun the player. */
	UPROPERTY(Config, EditAnywhere, Category = "Player|Falling")
	float StunFallHeights = 2.f;

	/** Falls higher than this many player heights kill the player. */
	UPROPERTY(Config, EditAnywhere, Category = "Player|Falling")
	float DeathFallHeights = 3.f;

	UPROPERTY(Config, EditAnywhere, Category = "Player|Falling", meta = (Units = "s"))
	float StunDuration = 2.f;

	UPROPERTY(Config, EditAnywhere, Category = "Player|Movement")
	float WalkSpeed = 320.f;

	UPROPERTY(Config, EditAnywhere, Category = "Player|Movement")
	float SprintSpeed = 560.f;

	UPROPERTY(Config, EditAnywhere, Category = "Player|Movement")
	float CrouchSpeed = 160.f;

	/** Gamepad look speed in degrees per second at full stick deflection. */
	UPROPERTY(Config, EditAnywhere, Category = "Player|Movement")
	float GamepadLookRate = 160.f;

	UPROPERTY(Config, EditAnywhere, Category = "Player|Interaction", meta = (Units = "cm"))
	float InteractDistance = 220.f;

	UPROPERTY(Config, EditAnywhere, Category = "Player|Interaction", meta = (Units = "cm"))
	float HoldDistance = 140.f;

	UPROPERTY(Config, EditAnywhere, Category = "Player|Interaction", meta = (Units = "kg"))
	float MaxGrabMass = 40.f;

	UPROPERTY(Config, EditAnywhere, Category = "Player|Interaction")
	float ThrowSpeed = 1100.f;

	UPROPERTY(Config, EditAnywhere, Category = "Player|Inventory")
	int32 InventorySlots = 12;

	// --- Noise --------------------------------------------------------------

	UPROPERTY(Config, EditAnywhere, Category = "Noise", meta = (Units = "cm"))
	float WalkNoiseRange = 700.f;

	UPROPERTY(Config, EditAnywhere, Category = "Noise", meta = (Units = "cm"))
	float SprintNoiseRange = 1600.f;

	UPROPERTY(Config, EditAnywhere, Category = "Noise", meta = (Units = "cm"))
	float LandingNoiseRange = 1200.f;

	UPROPERTY(Config, EditAnywhere, Category = "Noise", meta = (Units = "cm"))
	float ImpactNoiseRange = 1500.f;

	UPROPERTY(Config, EditAnywhere, Category = "Noise", meta = (Units = "s"))
	float FootstepNoiseInterval = 0.45f;

	// --- Guest --------------------------------------------------------------

	UPROPERTY(Config, EditAnywhere, Category = "Guest|Senses", meta = (Units = "cm"))
	float SightRadius = 1800.f;

	UPROPERTY(Config, EditAnywhere, Category = "Guest|Senses", meta = (Units = "cm"))
	float LoseSightRadius = 2300.f;

	UPROPERTY(Config, EditAnywhere, Category = "Guest|Senses", meta = (Units = "deg"))
	float PeripheralVisionHalfAngle = 65.f;

	UPROPERTY(Config, EditAnywhere, Category = "Guest|Senses", meta = (Units = "cm"))
	float HearingRange = 3000.f;

	/** Inside a dark zone the player is only noticed closer than this. */
	UPROPERTY(Config, EditAnywhere, Category = "Guest|Senses", meta = (Units = "cm"))
	float DarkZoneDetectDistance = 250.f;

	UPROPERTY(Config, EditAnywhere, Category = "Guest|Behaviour", meta = (Units = "cm"))
	float CatchDistance = 110.f;

	UPROPERTY(Config, EditAnywhere, Category = "Guest|Behaviour")
	float PatrolSpeed = 230.f;

	UPROPERTY(Config, EditAnywhere, Category = "Guest|Behaviour")
	float ChaseSpeed = 480.f;

	/** Alert is 0..100. Seeing the player sets it to 100. */
	UPROPERTY(Config, EditAnywhere, Category = "Guest|Behaviour")
	float AlertDecayPerSecond = 6.f;

	/** Alert added by a noise of loudness 1. */
	UPROPERTY(Config, EditAnywhere, Category = "Guest|Behaviour")
	float HearingAlertGain = 35.f;

	/** Below this alert the Guest gives up searching and returns to patrol. */
	UPROPERTY(Config, EditAnywhere, Category = "Guest|Behaviour")
	float CalmAlert = 15.f;

	/** Seconds without seeing the player before a chase turns into a search. */
	UPROPERTY(Config, EditAnywhere, Category = "Guest|Behaviour", meta = (Units = "s"))
	float LoseTargetTime = 2.f;

	UPROPERTY(Config, EditAnywhere, Category = "Guest|Behaviour", meta = (Units = "s"))
	float SearchDuration = 12.f;

	UPROPERTY(Config, EditAnywhere, Category = "Guest|Behaviour", meta = (Units = "cm"))
	float SearchRadius = 700.f;

	UPROPERTY(Config, EditAnywhere, Category = "Guest|Behaviour", meta = (Units = "s"))
	float PatrolWaitMin = 1.5f;

	UPROPERTY(Config, EditAnywhere, Category = "Guest|Behaviour", meta = (Units = "s"))
	float PatrolWaitMax = 4.f;

	/** How long the space gun keeps the Guest dissolved. */
	UPROPERTY(Config, EditAnywhere, Category = "Guest|Behaviour", meta = (Units = "s"))
	float NeutralizeDuration = 1.5f;

	/** Progress flags that raise the Guest's activity phase (see Docs/PLAN.md). */
	UPROPERTY(Config, EditAnywhere, Category = "Guest|Phases")
	TArray<FHGGuestPhaseRule> GuestPhaseRules;

	// --- Guest model ----------------------------------------------------------
	// Filled by Scripts/Editor/import_characters.py. Empty = grey placeholder cylinder.

	UPROPERTY(Config, EditAnywhere, Category = "Guest|Model")
	TSoftObjectPtr<USkeletalMesh> GuestMesh;

	/** Extra parts on the same skeleton (the cloak); they follow the main mesh's animation. */
	UPROPERTY(Config, EditAnywhere, Category = "Guest|Model")
	TArray<TSoftObjectPtr<USkeletalMesh>> GuestExtraMeshes;

	UPROPERTY(Config, EditAnywhere, Category = "Guest|Model")
	TSoftObjectPtr<UAnimSequence> GuestIdleAnim;

	/** Optional: when empty, the run animation is played slower for walking. */
	UPROPERTY(Config, EditAnywhere, Category = "Guest|Model")
	TSoftObjectPtr<UAnimSequence> GuestWalkAnim;

	UPROPERTY(Config, EditAnywhere, Category = "Guest|Model")
	TSoftObjectPtr<UAnimSequence> GuestRunAnim;

	UPROPERTY(Config, EditAnywhere, Category = "Guest|Model")
	TSoftObjectPtr<UAnimSequence> GuestSearchAnim;

	UPROPERTY(Config, EditAnywhere, Category = "Guest|Model")
	TSoftObjectPtr<UAnimSequence> GuestCatchAnim;

	/** Rotation that makes an imported mesh face the actor's forward axis. */
	UPROPERTY(Config, EditAnywhere, Category = "Guest|Model", meta = (Units = "deg"))
	float CharacterMeshYawOffset = -90.f;

	/** Used by the import script; also writes the values to Config/DefaultGame.ini. */
	UFUNCTION(BlueprintCallable, Category = "Hello Guest|Settings")
	static void SetGuestAssets(USkeletalMesh* Mesh, const TArray<USkeletalMesh*>& ExtraMeshes, UAnimSequence* Idle, UAnimSequence* Walk, UAnimSequence* Run,
		UAnimSequence* Search, UAnimSequence* Catch);

	// --- Death --------------------------------------------------------------

	UPROPERTY(Config, EditAnywhere, Category = "Death", meta = (Units = "s"))
	float CaughtRespawnDelay = 2.2f;

	UPROPERTY(Config, EditAnywhere, Category = "Death", meta = (Units = "s"))
	float FallRespawnDelay = 1.5f;

	/** One of these is picked at random when the Guest catches the player. */
	UPROPERTY(Config, EditAnywhere, Category = "Death")
	TArray<TSoftObjectPtr<USoundBase>> ScreamerSounds;

	/** PlayerStartTag of the respawn point at the player's house. */
	UPROPERTY(Config, EditAnywhere, Category = "Death")
	FName HomeSpawnTag = TEXT("HomeSpawn");

	// --- Saving -------------------------------------------------------------

	UPROPERTY(Config, EditAnywhere, Category = "Saving")
	int32 SaveSlotCount = 3;

	UPROPERTY(Config, EditAnywhere, Category = "Saving", meta = (Units = "s"))
	float AutosaveRetryDelay = 2.f;

	/** Flags that count towards the completion percentage shown on save slots. */
	UPROPERTY(Config, EditAnywhere, Category = "Saving")
	TArray<FName> ProgressFlags;

	// --- Language -----------------------------------------------------------

	/** Cultures offered in the settings menu. The first one is the fallback. */
	UPROPERTY(Config, EditAnywhere, Category = "Language")
	TArray<FString> SupportedCultures;
};
