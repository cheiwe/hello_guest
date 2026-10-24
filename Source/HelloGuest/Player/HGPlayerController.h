#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "HGPlayerController.generated.h"

class UHGInputConfig;
class FHGInputDeviceProcessor;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FHGOnInputDeviceChanged, bool, bUsingGamepad);

UCLASS()
class HELLOGUEST_API AHGPlayerController : public APlayerController
{
	GENERATED_BODY()

public:
	UHGInputConfig* GetInputConfig();

	/** True when the last input came from a gamepad; UI uses it to show button or key prompts. */
	UFUNCTION(BlueprintPure, Category = "Hello Guest|Input")
	bool IsUsingGamepad() const { return bUsingGamepad; }

	/** Short label of the interact button for the current device ("E" or "X"). */
	FText GetInteractKeyLabel() const;

	void TogglePauseMenu();

	UPROPERTY(BlueprintAssignable, Category = "Hello Guest|Input")
	FHGOnInputDeviceChanged OnInputDeviceChanged;

	// --- Console commands for testing (slots are 1-based) ---------------------
	UFUNCTION(Exec) void HGSave();
	UFUNCTION(Exec) void HGLoad(int32 Slot);
	UFUNCTION(Exec) void HGNewGame(int32 Slot);
	UFUNCTION(Exec) void HGSlots();
	UFUNCTION(Exec) void HGLanguage(const FString& Culture);
	UFUNCTION(Exec) void HGGive(FName ItemId);
	UFUNCTION(Exec) void HGFlag(FName Flag);
	/** Toggles god mode (also the G key): the Guest cannot catch the player. */
	UFUNCTION(Exec) void HGGod();

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
	void SetUsingGamepad(bool bGamepad);

	UPROPERTY()
	TObjectPtr<UHGInputConfig> InputConfig;

	TSharedPtr<FHGInputDeviceProcessor> DeviceProcessor;
	bool bUsingGamepad = false;
};
