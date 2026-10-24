#pragma once

#include "CoreMinimal.h"
#include "HGTypes.generated.h"

/** Item identifiers used across the game. Items are referenced by FName so that levels and saves stay readable. */
namespace HGItems
{
	inline const FName Crowbar(TEXT("Crowbar"));
	inline const FName Scissors(TEXT("Scissors"));
	inline const FName UpstairsKey(TEXT("UpstairsKey"));
	inline const FName KeyRed(TEXT("KeyRed"));
	inline const FName KeyBlue(TEXT("KeyBlue"));
	inline const FName KeyYellow(TEXT("KeyYellow"));
	inline const FName KeyGreen(TEXT("KeyGreen"));
	inline const FName Fuse(TEXT("Fuse"));
	inline const FName Bulb(TEXT("Bulb"));
	inline const FName Antenna(TEXT("Antenna"));
	inline const FName SpaceGun(TEXT("SpaceGun"));
}

/** Helpers for world-state flag names ("Item.Crowbar", "Lock.ChainRed", ...). */
namespace HGFlags
{
	inline FName Item(FName ItemId) { return FName(*FString::Printf(TEXT("Item.%s"), *ItemId.ToString())); }
	inline FName Lock(FName LockId) { return FName(*FString::Printf(TEXT("Lock.%s"), *LockId.ToString())); }
}

UENUM(BlueprintType)
enum class EHGGuestState : uint8
{
	Patrol,
	Investigate,
	Chase,
	Search,
	Incapacitated,
	/** The player escaped to a safe zone: the Guest shows his frustration, then goes back to patrol. */
	GiveUp
};

UENUM(BlueprintType)
enum class EHGDeathReason : uint8
{
	Fall,
	Caught
};

USTRUCT(BlueprintType)
struct FHGInventoryEntry
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, SaveGame, Category = "Inventory")
	FName ItemId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, SaveGame, Category = "Inventory")
	int32 Count = 0;
};

/** When the flag is set, the Guest switches to at least this activity phase. */
USTRUCT(BlueprintType)
struct FHGGuestPhaseRule
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Guest")
	FName Flag;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Guest")
	int32 Phase = 0;

	/** Movement speed multiplier while this phase is active. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Guest")
	float SpeedMultiplier = 1.f;
};
