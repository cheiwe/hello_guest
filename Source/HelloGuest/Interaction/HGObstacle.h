#pragma once

#include "CoreMinimal.h"
#include "Interaction/HGInteractableBase.h"
#include "HGObstacle.generated.h"

/**
 * Something that blocks the way until removed with an item: boards (crowbar), police tape and
 * spider web (scissors), a window to break. Disappears when cleared.
 */
UCLASS()
class HELLOGUEST_API AHGObstacle : public AHGInteractableBase
{
	GENERATED_BODY()

public:
	AHGObstacle();

	virtual bool CanInteract_Implementation(AHGPlayerCharacter* Player) const override;
	virtual void Interact_Implementation(AHGPlayerCharacter* Player) override;

	UFUNCTION(BlueprintPure, Category = "Obstacle")
	bool IsCleared() const { return bCleared; }

protected:
	virtual void ApplyState() override;

	/** Spider scare, splinters, glass shards... */
	UFUNCTION(BlueprintImplementableEvent, Category = "Obstacle")
	void OnCleared(AHGPlayerCharacter* Player);

	/** 0 = silent (cutting tape), 1 = very loud (breaking boards or glass). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Obstacle")
	float NoiseLoudness = 0.8f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Obstacle", meta = (Units = "cm"))
	float NoiseRange = 1500.f;

	UPROPERTY(SaveGame, BlueprintReadOnly, Category = "Obstacle")
	bool bCleared = false;
};
