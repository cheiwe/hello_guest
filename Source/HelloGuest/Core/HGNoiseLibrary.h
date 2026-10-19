#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "HGNoiseLibrary.generated.h"

UCLASS()
class HELLOGUEST_API UHGNoiseLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/** Reports a noise the Guest can hear. Loudness 0..1 scales how alarmed he gets. */
	UFUNCTION(BlueprintCallable, Category = "Hello Guest|Noise", meta = (WorldContext = "WorldContextObject"))
	static void MakeNoiseAt(const UObject* WorldContextObject, FVector Location, float Loudness, float Range, AActor* Instigator);
};
