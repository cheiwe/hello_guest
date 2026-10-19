#pragma once

#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "Core/HGTypes.h"
#include "HGSaveGame.generated.h"

USTRUCT()
struct FHGActorSaveRecord
{
	GENERATED_BODY()

	UPROPERTY()
	FName ActorName;

	UPROPERTY()
	TArray<uint8> Data;
};

USTRUCT(BlueprintType)
struct FHGSaveSlotInfo
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "Save")
	int32 SlotIndex = INDEX_NONE;

	UPROPERTY(BlueprintReadOnly, Category = "Save")
	bool bExists = false;

	UPROPERTY(BlueprintReadOnly, Category = "Save")
	bool bAutosave = false;

	UPROPERTY(BlueprintReadOnly, Category = "Save")
	FDateTime Timestamp;

	UPROPERTY(BlueprintReadOnly, Category = "Save")
	float PlayTimeSeconds = 0.f;

	UPROPERTY(BlueprintReadOnly, Category = "Save")
	float ProgressPercent = 0.f;

	/** PNG screenshot for the slot card; empty if none was captured. */
	UPROPERTY(BlueprintReadOnly, Category = "Save")
	TArray<uint8> ThumbnailPng;
};

UCLASS()
class HELLOGUEST_API UHGSaveGame : public USaveGame
{
	GENERATED_BODY()

public:
	/** Bump when the layout changes and handle the old version in Migrate(). */
	static constexpr int32 LatestVersion = 1;

	void Migrate();

	UPROPERTY()
	int32 Version = LatestVersion;

	UPROPERTY()
	bool bAutosave = false;

	UPROPERTY()
	FDateTime Timestamp;

	UPROPERTY()
	float PlayTimeSeconds = 0.f;

	UPROPERTY()
	float ProgressPercent = 0.f;

	UPROPERTY()
	TArray<uint8> ThumbnailPng;

	UPROPERTY()
	FString MapPackage;

	UPROPERTY()
	TArray<FName> Flags;

	UPROPERTY()
	TMap<FName, int32> Values;

	UPROPERTY()
	TArray<FHGInventoryEntry> Inventory;

	UPROPERTY()
	int32 SelectedInventoryIndex = INDEX_NONE;

	UPROPERTY()
	FTransform PlayerTransform;

	UPROPERTY()
	FRotator ControlRotation = FRotator::ZeroRotator;

	UPROPERTY()
	TArray<FHGActorSaveRecord> Actors;
};
