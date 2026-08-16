#pragma once

#include "CoreMinimal.h"
#include "SkyguardGunshipSortieDirector.h"
#include "SkyguardGunshipTypes.h"

class UObject;
class USkyguardRadioChatterComponent;

/**
 * Thin Harbor Breaker beat → pilot-call bridge.
 * Reuses SkyguardPilotVoice + USkyguardRadioChatterComponent. No VO bank.
 */
namespace SkyguardHarborBeatCalls
{
	bool TryLineForBeat(ESkyguardSortieBeat Beat, ESkyguardPilotLine& OutLine);
	ESkyguardPilotLine InboundLine();
	ESkyguardPilotLine GoThermalLine();

	/** CallEvent the Harbor beat line. Enqueues when Radio is on the context actor. */
	bool ApplyBeat(
		UObject* WorldContext,
		ESkyguardSortieBeat Beat,
		USkyguardRadioChatterComponent* Radio = nullptr);

	bool ApplyInbound(
		UObject* WorldContext,
		USkyguardRadioChatterComponent* Radio = nullptr);

	bool ApplyGoThermal(
		UObject* WorldContext,
		USkyguardRadioChatterComponent* Radio = nullptr);
}
