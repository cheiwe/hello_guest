#include "Core/HGNoiseLibrary.h"
#include "Engine/World.h"
#include "Perception/AISense_Hearing.h"

void UHGNoiseLibrary::MakeNoiseAt(const UObject* WorldContextObject, FVector Location, float Loudness, float Range, AActor* Instigator)
{
	UWorld* World = WorldContextObject ? WorldContextObject->GetWorld() : nullptr;
	if (!World || Loudness <= 0.f)
	{
		return;
	}

	UAISense_Hearing::ReportNoiseEvent(World, Location, Loudness, Instigator, Range);
}
