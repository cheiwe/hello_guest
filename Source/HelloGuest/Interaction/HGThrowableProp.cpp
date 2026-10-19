#include "Interaction/HGThrowableProp.h"
#include "Core/HGGameplaySettings.h"
#include "Core/HGNoiseLibrary.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "UObject/ConstructorHelpers.h"

AHGThrowableProp::AHGThrowableProp()
{
	PrimaryActorTick.bCanEverTick = false;

	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	SetRootComponent(Mesh);

	static ConstructorHelpers::FObjectFinder<UStaticMesh> Placeholder(TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (Placeholder.Succeeded())
	{
		Mesh->SetStaticMesh(Placeholder.Object);
		Mesh->SetRelativeScale3D(FVector(0.2f));
	}

	Mesh->SetMobility(EComponentMobility::Movable);
	Mesh->SetCollisionProfileName(TEXT("PhysicsActor"));
	Mesh->SetSimulatePhysics(true);
	Mesh->SetNotifyRigidBodyCollision(true);
}

void AHGThrowableProp::BeginPlay()
{
	Super::BeginPlay();
	Mesh->OnComponentHit.AddDynamic(this, &AHGThrowableProp::HandleHit);
}

void AHGThrowableProp::HandleHit(UPrimitiveComponent* HitComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, FVector NormalImpulse, const FHitResult& Hit)
{
	const double Now = GetWorld()->GetTimeSeconds();
	if (Now - LastNoiseTime < 0.3 || Mesh->GetPhysicsLinearVelocity().Size() < NoiseSpeedThreshold)
	{
		return;
	}

	LastNoiseTime = Now;
	UHGNoiseLibrary::MakeNoiseAt(this, GetActorLocation(), NoiseLoudness, UHGGameplaySettings::Get()->ImpactNoiseRange, this);
}
