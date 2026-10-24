#pragma once

#include "CoreMinimal.h"
#include "AIController.h"
#include "Core/HGTypes.h"
#include "Perception/AIPerceptionTypes.h"
#include "HGGuestAIController.generated.h"

class AHGPlayerCharacter;
class AHGGuestCharacter;
class UAISenseConfig_Sight;
class UAISenseConfig_Hearing;
class UNavigationQueryFilter;

/**
 * Guest behaviour as a small state machine:
 * Patrol -> (noise) Investigate -> Search -> Patrol
 * any    -> (sees player) Chase -> (lost) Search / (close) catch / (player in a safe zone) GiveUp -> Patrol.
 * Alert (0..100) rises with noises and decays over time; seeing the player sets it to 100.
 */
UCLASS()
class HELLOGUEST_API AHGGuestAIController : public AAIController
{
	GENERATED_BODY()

public:
	AHGGuestAIController();

	virtual void Tick(float DeltaSeconds) override;
	virtual void OnMoveCompleted(FAIRequestID RequestID, const FPathFollowingResult& Result) override;

	UFUNCTION(BlueprintPure, Category = "Hello Guest|Guest")
	EHGGuestState GetGuestState() const { return State; }

	UFUNCTION(BlueprintPure, Category = "Hello Guest|Guest")
	float GetAlert() const { return Alert; }

	bool IsChasing() const { return State == EHGGuestState::Chase; }

	void SetIncapacitated(bool bValue);
	void ResetToPatrol();

protected:
	virtual void BeginPlay() override;
	virtual void OnPossess(APawn* InPawn) override;

	UFUNCTION()
	void HandlePerception(AActor* Actor, FAIStimulus Stimulus);

	UPROPERTY(VisibleAnywhere, Category = "AI")
	TObjectPtr<UAISenseConfig_Sight> SightConfig;

	UPROPERTY(VisibleAnywhere, Category = "AI")
	TObjectPtr<UAISenseConfig_Hearing> HearingConfig;

private:
	AHGGuestCharacter* GetGuest() const;
	void EnterState(EHGGuestState NewState);
	void StartChase(AHGPlayerCharacter* Player);
	void MoveToNextPatrolPoint();
	void MoveToSearchPoint();
	void TickChase(float DeltaSeconds);
	void CatchPlayer();
	void GiveUp();
	void UpdateSpeed();

	/** Arrived (or already standing) at the move goal: wait, look around or pick the next point. Never starts a move itself. */
	void HandleMoveFinished();

	/**
	 * MoveToLocation that retries later instead of freezing when no path can be requested.
	 * Without bAllowPartialPath an unreachable destination fails instead of walking to the nearest
	 * reachable spot, so patrols skip points that are boarded up.
	 */
	void RequestMove(const FVector& Destination, float AcceptanceRadius, TSubclassOf<UNavigationQueryFilter> Filter, bool bProjectToNavigation,
		bool bAllowPartialPath = true);

	/** Applies the dark-zone and safe-zone rules on top of the engine's line-of-sight check. */
	bool CanNoticePlayer(const AHGPlayerCharacter* Player) const;

	/** Close range: sees the player in any posture outside the vision cone, unless something blocks the view. */
	bool CanSeePlayerUpClose(const AHGPlayerCharacter* Player) const;

	/** Unblocked view from the Guest's eyes to the player's body or head. */
	bool HasClearViewTo(const AHGPlayerCharacter* Player) const;

	AHGPlayerCharacter* GetLocalPlayerCharacter() const;

	EHGGuestState State = EHGGuestState::Patrol;
	EHGGuestState StateBeforeIncapacitated = EHGGuestState::Patrol;
	TWeakObjectPtr<AHGPlayerCharacter> Target;
	TWeakObjectPtr<AHGPlayerCharacter> PlayerInSight;
	FVector LastKnownLocation = FVector::ZeroVector;
	float Alert = 0.f;
	float StateTime = 0.f;
	float TimeSinceSeen = 0.f;
	float WaitRemaining = 0.f;
	float RepathCooldown = 0.f;
	bool bWarnedNoNavMesh = false;
	bool bCaught = false;

	/** True after a chase: searching may then follow the player into restricted rooms. */
	bool bAllowRestricted = false;
};
