#pragma once

#include "CoreMinimal.h"
#include "Commandlets/Commandlet.h"
#include "SkyguardPsoStableKeyFilterCommandlet.generated.h"

/**
 * Produces a minimal stable-key file containing only shaders referenced by
 * recorded PSO caches. This avoids serializing thousands of unrelated keys
 * into UE 5.8 binary stable-cache files.
 */
UCLASS()
class SKYGUARD52_API USkyguardPsoStableKeyFilterCommandlet final : public UCommandlet
{
	GENERATED_BODY()

public:
	USkyguardPsoStableKeyFilterCommandlet();

	virtual int32 Main(const FString& Params) override;
};
