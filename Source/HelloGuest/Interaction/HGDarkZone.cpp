#include "Interaction/HGDarkZone.h"
#include "Player/HGPlayerCharacter.h"
#include "Components/BoxComponent.h"

AHGDarkZone::AHGDarkZone()
{
	PrimaryActorTick.bCanEverTick = false;

	Volume = CreateDefaultSubobject<UBoxComponent>(TEXT("Volume"));
	Volume->SetBoxExtent(FVector(150.f));
	Volume->SetCollisionProfileName(TEXT("Trigger"));
	Volume->SetCanEverAffectNavigation(false);
	Volume->ShapeColor = FColor(40, 40, 80);
	SetRootComponent(Volume);
}

void AHGDarkZone::BeginPlay()
{
	Super::BeginPlay();
	Volume->OnComponentBeginOverlap.AddDynamic(this, &AHGDarkZone::HandleBeginOverlap);
	Volume->OnComponentEndOverlap.AddDynamic(this, &AHGDarkZone::HandleEndOverlap);
}

void AHGDarkZone::HandleBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp,
	int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (AHGPlayerCharacter* Player = Cast<AHGPlayerCharacter>(OtherActor))
	{
		Player->EnterDarkZone();
	}
}

void AHGDarkZone::HandleEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex)
{
	if (AHGPlayerCharacter* Player = Cast<AHGPlayerCharacter>(OtherActor))
	{
		Player->ExitDarkZone();
	}
}
