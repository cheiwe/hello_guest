#include "Player/HGInventoryComponent.h"
#include "Core/HGGameplaySettings.h"

UHGInventoryComponent::UHGInventoryComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
}

int32 UHGInventoryComponent::FindIndex(FName ItemId) const
{
	return Entries.IndexOfByPredicate([ItemId](const FHGInventoryEntry& Entry) { return Entry.ItemId == ItemId; });
}

bool UHGInventoryComponent::AddItem(FName ItemId, int32 Count)
{
	if (ItemId.IsNone() || Count <= 0)
	{
		return false;
	}

	int32 Index = FindIndex(ItemId);
	if (Index == INDEX_NONE)
	{
		if (Entries.Num() >= UHGGameplaySettings::Get()->InventorySlots)
		{
			return false;
		}
		FHGInventoryEntry NewEntry;
		NewEntry.ItemId = ItemId;
		Index = Entries.Add(NewEntry);
	}

	Entries[Index].Count += Count;
	SelectedIndex = Index;
	OnInventoryChanged.Broadcast();
	return true;
}

bool UHGInventoryComponent::RemoveItem(FName ItemId, int32 Count)
{
	const int32 Index = FindIndex(ItemId);
	if (Index == INDEX_NONE || Entries[Index].Count < Count)
	{
		return false;
	}

	Entries[Index].Count -= Count;
	if (Entries[Index].Count <= 0)
	{
		Entries.RemoveAt(Index);
		SelectedIndex = Entries.IsEmpty() ? INDEX_NONE : FMath::Clamp(SelectedIndex, 0, Entries.Num() - 1);
	}
	OnInventoryChanged.Broadcast();
	return true;
}

bool UHGInventoryComponent::HasItem(FName ItemId, int32 Count) const
{
	return GetItemCount(ItemId) >= Count;
}

int32 UHGInventoryComponent::GetItemCount(FName ItemId) const
{
	const int32 Index = FindIndex(ItemId);
	return Index == INDEX_NONE ? 0 : Entries[Index].Count;
}

FName UHGInventoryComponent::GetSelectedItem() const
{
	return Entries.IsValidIndex(SelectedIndex) ? Entries[SelectedIndex].ItemId : NAME_None;
}

void UHGInventoryComponent::SelectNext()
{
	if (!Entries.IsEmpty())
	{
		SelectedIndex = (SelectedIndex + 1) % Entries.Num();
		OnInventoryChanged.Broadcast();
	}
}

void UHGInventoryComponent::SelectPrevious()
{
	if (!Entries.IsEmpty())
	{
		SelectedIndex = (SelectedIndex - 1 + Entries.Num()) % Entries.Num();
		OnInventoryChanged.Broadcast();
	}
}

void UHGInventoryComponent::SetEntries(const TArray<FHGInventoryEntry>& InEntries, int32 InSelectedIndex)
{
	Entries = InEntries;
	SelectedIndex = Entries.IsValidIndex(InSelectedIndex) ? InSelectedIndex : (Entries.IsEmpty() ? INDEX_NONE : 0);
	OnInventoryChanged.Broadcast();
}
