#include "Interaction/HGInteractableBase.h"
#include "Player/HGPlayerCharacter.h"
#include "Player/HGInventoryComponent.h"
#include "Core/HGItemLibrary.h"
#include "Core/HGNoiseLibrary.h"
#include "Core/HGWorldStateSubsystem.h"
#include "Components/StaticMeshComponent.h"

#define LOCTEXT_NAMESPACE "HGInteraction"

AHGInteractableBase::AHGInteractableBase()
{
	PrimaryActorTick.bCanEverTick = false;

	Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	SetRootComponent(Root);

	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	Mesh->SetupAttachment(Root);
	Mesh->SetCollisionProfileName(TEXT("BlockAll"));

	InteractionText = LOCTEXT("Use", "Use");
}

void AHGInteractableBase::BeginPlay()
{
	Super::BeginPlay();
	ApplyState();
}

bool AHGInteractableBase::HasRequiredItem(const AHGPlayerCharacter* Player) const
{
	return RequiredItem.IsNone() || (Player && Player->GetInventory()->HasItem(RequiredItem));
}

FText AHGInteractableBase::GetMissingItemText() const
{
	return FText::Format(LOCTEXT("Needs", "Needs: {0}"), UHGItemLibrary::GetItemDisplayName(RequiredItem));
}

void AHGInteractableBase::SetWorldFlag(FName Flag) const
{
	if (UHGWorldStateSubsystem* WorldState = UHGWorldStateSubsystem::Get(this))
	{
		WorldState->SetFlag(Flag);
	}
}

void AHGInteractableBase::EmitNoise(float Loudness, float Range)
{
	UHGNoiseLibrary::MakeNoiseAt(this, GetActorLocation(), Loudness, Range, this);
}

bool AHGInteractableBase::CanInteract_Implementation(AHGPlayerCharacter* Player) const
{
	return HasRequiredItem(Player);
}

void AHGInteractableBase::Interact_Implementation(AHGPlayerCharacter* Player)
{
	if (bConsumeRequiredItem && !RequiredItem.IsNone())
	{
		Player->GetInventory()->RemoveItem(RequiredItem);
	}

	OnInteracted(Player);
	SetWorldFlag(FlagOnUse);
}

FText AHGInteractableBase::GetInteractionText_Implementation(AHGPlayerCharacter* Player) const
{
	return HasRequiredItem(Player) ? InteractionText : GetMissingItemText();
}

void AHGInteractableBase::OnStateRestored_Implementation()
{
	ApplyState();
}

#undef LOCTEXT_NAMESPACE
