#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "HGGuestCharacter.generated.h"

class UStaticMeshComponent;

/** The Guest. Behaviour lives in AHGGuestAIController; this class holds the body, speed and status effects. */
UCLASS()
class HELLOGUEST_API AHGGuestCharacter : public ACharacter
{
	GENERATED_BODY()

public:
	AHGGuestCharacter();

	UFUNCTION(BlueprintPure, Category = "Hello Guest|Guest")
	bool IsChasing() const;

	UFUNCTION(BlueprintPure, Category = "Hello Guest|Guest")
	bool IsIncapacitated() const { return bIncapacitated; }

	/** Base speed from the controller, scaled by the current slow effect. */
	void SetBaseSpeed(float Speed);

	/** Trap hit: bear trap, bucket on the head... */
	UFUNCTION(BlueprintCallable, Category = "Hello Guest|Guest")
	void Stun(float Duration);

	/** Glue puddle and similar. */
	UFUNCTION(BlueprintCallable, Category = "Hello Guest|Guest")
	void ApplySlow(float SpeedMultiplier, float Duration);

	/** Space gun hit: dissolves like a ghost and comes back after NeutralizeDuration. */
	UFUNCTION(BlueprintCallable, Category = "Hello Guest|Guest")
	void Neutralize();

	/** Back to the spawn point and calm, used after the player respawns or loads a save. */
	void ResetToHome();

	UFUNCTION(BlueprintImplementableEvent, Category = "Hello Guest|Guest")
	void OnChaseStarted();

	UFUNCTION(BlueprintImplementableEvent, Category = "Hello Guest|Guest")
	void OnCaughtPlayer();

	UFUNCTION(BlueprintImplementableEvent, Category = "Hello Guest|Guest")
	void OnStunned(float Duration);

	UFUNCTION(BlueprintImplementableEvent, Category = "Hello Guest|Guest")
	void OnNeutralized(bool bDissolved);

protected:
	virtual void BeginPlay() override;

	/** Grey stand-in until the real skeletal mesh is imported. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStaticMeshComponent> PlaceholderBody;

private:
	void SetIncapacitated(bool bValue);
	void EndStun();
	void EndSlow();
	void EndNeutralize();

	FTransform HomeTransform;
	float BaseSpeed = 0.f;
	float SlowMultiplier = 1.f;
	bool bIncapacitated = false;

	FTimerHandle StunTimer;
	FTimerHandle SlowTimer;
	FTimerHandle NeutralizeTimer;
};
