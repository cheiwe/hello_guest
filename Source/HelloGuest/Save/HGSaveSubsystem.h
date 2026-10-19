#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Save/HGSaveGame.h"
#include "HGSaveSubsystem.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FHGOnGameSaved, int32, SlotIndex, bool, bAutosave);

/**
 * Save slots. Every slot keeps a manual save and an autosave; "Continue"/LoadSlot picks the newer one.
 * Autosaves happen whenever a world-state flag is set (item taken, puzzle solved, lock opened),
 * but never during a chase. Slot indices are 0-based.
 */
UCLASS()
class HELLOGUEST_API UHGSaveSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	static UHGSaveSubsystem* Get(const UObject* WorldContextObject);

	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual void Deinitialize() override;

	/** Resets progress, binds the game to the slot and opens the game map. Does not delete old saves until the first save. */
	UFUNCTION(BlueprintCallable, Category = "Hello Guest|Save")
	void StartNewGame(int32 SlotIndex);

	/** Manual save into the current slot. Fails during a chase or while the player is dead. */
	UFUNCTION(BlueprintCallable, Category = "Hello Guest|Save")
	bool ManualSave();

	/** Loads the newest save (manual or auto) of the slot. */
	UFUNCTION(BlueprintCallable, Category = "Hello Guest|Save")
	bool LoadSlot(int32 SlotIndex);

	/** Loads the newest save of all slots. */
	UFUNCTION(BlueprintCallable, Category = "Hello Guest|Save")
	bool ContinueLastGame();

	UFUNCTION(BlueprintCallable, Category = "Hello Guest|Save")
	void DeleteSlot(int32 SlotIndex);

	UFUNCTION(BlueprintPure, Category = "Hello Guest|Save")
	FHGSaveSlotInfo GetSlotInfo(int32 SlotIndex) const;

	UFUNCTION(BlueprintPure, Category = "Hello Guest|Save")
	int32 GetSlotCount() const;

	UFUNCTION(BlueprintPure, Category = "Hello Guest|Save")
	int32 GetCurrentSlot() const { return CurrentSlot; }

	UFUNCTION(BlueprintPure, Category = "Hello Guest|Save")
	bool CanSaveNow() const;

	UFUNCTION(BlueprintPure, Category = "Hello Guest|Save")
	float GetPlayTimeSeconds() const;

	UPROPERTY(BlueprintAssignable, Category = "Hello Guest|Save")
	FHGOnGameSaved OnGameSaved;

private:
	static FString MakeSlotName(int32 SlotIndex, bool bAutosave);

	bool SaveToSlot(int32 SlotIndex, bool bAutosave);
	UHGSaveGame* LoadSaveObject(int32 SlotIndex, bool bAutosave) const;
	UHGSaveGame* LoadNewest(int32 SlotIndex) const;
	bool BeginLoad(UHGSaveGame* Save, int32 SlotIndex);

	UHGSaveGame* CaptureState(UWorld* World, bool bAutosave) const;
	void ApplyState(UWorld* World, UHGSaveGame* Save);

	UFUNCTION()
	void HandleFlagSet(FName Flag);

	void TryAutosave();
	void HandlePostLoadMap(UWorld* World);

	UWorld* GetGameWorld() const;

	int32 CurrentSlot = 0;
	float PlayTimeAtSessionStart = 0.f;
	double SessionStartRealTime = 0.0;

	UPROPERTY()
	TObjectPtr<UHGSaveGame> PendingLoad;

	FTimerHandle AutosaveTimer;
	FDelegateHandle PostLoadMapHandle;
};
