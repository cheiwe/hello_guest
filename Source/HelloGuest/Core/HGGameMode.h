#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "Core/HGTypes.h"
#include "HGGameMode.generated.h"

class AHGPlayerCharacter;
class AHGGuestCharacter;
class USoundBase;

/** Death, screamers and respawning at the player's house (inventory is kept). */
UCLASS()
class HELLOGUEST_API AHGGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	AHGGameMode();

	virtual void InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage) override;

	/** The Guest reached the player: face him, play a random screamer, then kill the player. */
	void HandlePlayerCaught(AHGGuestCharacter* Guest, AHGPlayerCharacter* Player);

	/** Called by the player on any death; schedules the respawn. */
	void HandlePlayerDied(AHGPlayerCharacter* Player, EHGDeathReason Reason);

	/** Close-up screamer animation / camera shake goes here. */
	UFUNCTION(BlueprintImplementableEvent, Category = "Hello Guest|Game")
	void OnScreamer(AHGGuestCharacter* Guest, AHGPlayerCharacter* Player);

	UFUNCTION(BlueprintImplementableEvent, Category = "Hello Guest|Game")
	void OnPlayerRespawned(AHGPlayerCharacter* Player);

protected:
	void RespawnPlayer(AHGPlayerCharacter* Player);
};
