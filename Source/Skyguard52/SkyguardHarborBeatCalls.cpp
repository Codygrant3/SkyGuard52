#include "SkyguardHarborBeatCalls.h"

#include "SkyguardPilotVoice.h"
#include "SkyguardRadioChatterComponent.h"

namespace
{
	UObject* ResolveVoiceContext(
		UObject* WorldContext,
		USkyguardRadioChatterComponent* Radio)
	{
		if (Radio && Radio->GetOwner())
		{
			return Radio->GetOwner();
		}
		return WorldContext;
	}
}

bool SkyguardHarborBeatCalls::TryLineForBeat(
	const ESkyguardSortieBeat Beat,
	ESkyguardPilotLine& OutLine)
{
	switch (Beat)
	{
	case ESkyguardSortieBeat::RadarNet:
		OutLine = ESkyguardPilotLine::RadarLit;
		return true;
	case ESkyguardSortieBeat::Choice:
		OutLine = ESkyguardPilotLine::Choice;
		return true;
	case ESkyguardSortieBeat::Extraction:
		OutLine = ESkyguardPilotLine::Extract;
		return true;
	default:
		return false;
	}
}

ESkyguardPilotLine SkyguardHarborBeatCalls::InboundLine()
{
	return ESkyguardPilotLine::Inbound;
}

ESkyguardPilotLine SkyguardHarborBeatCalls::GoThermalLine()
{
	return ESkyguardPilotLine::GoThermal;
}

bool SkyguardHarborBeatCalls::ApplyBeat(
	UObject* WorldContext,
	const ESkyguardSortieBeat Beat,
	USkyguardRadioChatterComponent* Radio)
{
	ESkyguardPilotLine Line = ESkyguardPilotLine::RadarLit;
	if (!TryLineForBeat(Beat, Line))
	{
		return false;
	}
	SkyguardPilotVoice::CallEvent(ResolveVoiceContext(WorldContext, Radio), Line);
	return true;
}

bool SkyguardHarborBeatCalls::ApplyInbound(
	UObject* WorldContext,
	USkyguardRadioChatterComponent* Radio)
{
	SkyguardPilotVoice::CallEvent(
		ResolveVoiceContext(WorldContext, Radio),
		InboundLine());
	return true;
}

bool SkyguardHarborBeatCalls::ApplyGoThermal(
	UObject* WorldContext,
	USkyguardRadioChatterComponent* Radio)
{
	SkyguardPilotVoice::CallEvent(
		ResolveVoiceContext(WorldContext, Radio),
		GoThermalLine());
	return true;
}
