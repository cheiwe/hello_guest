#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Core/HGTypes.h"
#include "HGInventoryComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FHGOnInventoryChanged);

/** Items the player carries. Keys are not consumed when used; bulbs and similar items stack. */
UCLASS(ClassGroup = (HelloGuest), meta = (BlueprintSpawnableComponent))
class HELLOGUEST_API UHGInventoryComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UHGInventoryComponent();

	UFUNCTION(BlueprintCallable, Category = "Hello Guest|Inventory")
	bool AddItem(FName ItemId, int32 Count = 1);

	UFUNCTION(BlueprintCallable, Category = "Hello Guest|Inventory")
	bool RemoveItem(FName ItemId, int32 Count = 1);

	UFUNCTION(BlueprintPure, Category = "Hello Guest|Inventory")
	bool HasItem(FName ItemId, int32 Count = 1) const;

	UFUNCTION(BlueprintPure, Category = "Hello Guest|Inventory")
	int32 GetItemCount(FName ItemId) const;

	UFUNCTION(BlueprintPure, Category = "Hello Guest|Inventory")
	FName GetSelectedItem() const;

	UFUNCTION(BlueprintCallable, Category = "Hello Guest|Inventory")
	void SelectNext();

	UFUNCTION(BlueprintCallable, Category = "Hello Guest|Inventory")
	void SelectPrevious();

	UFUNCTION(BlueprintPure, Category = "Hello Guest|Inventory")
	const TArray<FHGInventoryEntry>& GetEntries() const { return Entries; }

	int32 GetSelectedIndex() const { return SelectedIndex; }

	void SetEntries(const TArray<FHGInventoryEntry>& InEntries, int32 InSelectedIndex);

	UPROPERTY(BlueprintAssignable, Category = "Hello Guest|Inventory")
	FHGOnInventoryChanged OnInventoryChanged;

private:
	int32 FindIndex(FName ItemId) const;

	UPROPERTY()
	TArray<FHGInventoryEntry> Entries;

	int32 SelectedIndex = INDEX_NONE;
};
