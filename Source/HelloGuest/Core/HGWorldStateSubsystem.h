#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "HGWorldStateSubsystem.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FHGOnFlagSet, FName, Flag);

/**
 * Progress of the current playthrough: a set of flags ("Item.Crowbar", "Lock.ChainRed", ...)
 * and integer values (randomized safe digits and similar). Saved with every save slot.
 */
UCLASS()
class HELLOGUEST_API UHGWorldStateSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	static UHGWorldStateSubsystem* Get(const UObject* WorldContextObject);

	virtual void Initialize(FSubsystemCollectionBase& Collection) override;

	/** Clears progress and rolls the randomized puzzle values. */
	void ResetForNewGame();

	void RestoreState(const TArray<FName>& InFlags, const TMap<FName, int32>& InValues);

	UFUNCTION(BlueprintCallable, Category = "Hello Guest|World State")
	void SetFlag(FName Flag);

	UFUNCTION(BlueprintPure, Category = "Hello Guest|World State")
	bool HasFlag(FName Flag) const;

	UFUNCTION(BlueprintCallable, Category = "Hello Guest|World State")
	void SetValue(FName Key, int32 Value);

	UFUNCTION(BlueprintPure, Category = "Hello Guest|World State")
	int32 GetValue(FName Key, int32 DefaultValue = 0) const;

	/** Highest phase among the GuestPhaseRules whose flag is set. */
	UFUNCTION(BlueprintPure, Category = "Hello Guest|World State")
	int32 GetGuestPhase() const;

	float GetGuestSpeedMultiplier() const;

	/** 0..100, based on ProgressFlags in the gameplay settings. */
	UFUNCTION(BlueprintPure, Category = "Hello Guest|World State")
	float GetProgressPercent() const;

	TArray<FName> GetFlags() const { return Flags.Array(); }
	const TMap<FName, int32>& GetValues() const { return Values; }

	UPROPERTY(BlueprintAssignable, Category = "Hello Guest|World State")
	FHGOnFlagSet OnFlagSet;

	static const FName SafeDigit3;
	static const FName SafeDigit4;

private:
	UPROPERTY()
	TSet<FName> Flags;

	UPROPERTY()
	TMap<FName, int32> Values;
};
