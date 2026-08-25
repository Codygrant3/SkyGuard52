#include "SkyguardPilotVoice.h"

#include "Engine/Engine.h"
#include "Engine/World.h"

namespace
{
	void Say(UObject* WorldContext, const TCHAR* Line, const float Seconds)
	{
		if (!GEngine || !WorldContext || !WorldContext->GetWorld())
		{
			return;
		}
		GEngine->AddOnScreenDebugMessage(
			84711,
			Seconds,
			FLinearColor(1.f, 0.82f, 0.35f).ToFColor(true),
			FString::Printf(TEXT("PILOT: %s"), Line));
	}
}

void SkyguardPilotVoice::ConfirmCommand(
	UObject* WorldContext,
	const ESkyguardPilotCommand Command)
{
	switch (Command)
	{
	case ESkyguardPilotCommand::OrbitLeft:
		Say(WorldContext, TEXT("Coming left. Holding the circle."), 2.6f);
		break;
	case ESkyguardPilotCommand::OrbitRight:
		Say(WorldContext, TEXT("Coming right. Holding the circle."), 2.6f);
		break;
	case ESkyguardPilotCommand::AttackRun:
		Say(WorldContext, TEXT("Rolling in."), 2.2f);
		break;
	case ESkyguardPilotCommand::Break:
		Say(WorldContext, TEXT("Breaking off."), 2.2f);
		break;
	case ESkyguardPilotCommand::Extend:
		Say(WorldContext, TEXT("Opening the range."), 2.2f);
		break;
	case ESkyguardPilotCommand::Hold:
		Say(WorldContext, TEXT("Holding station."), 2.2f);
		break;
	case ESkyguardPilotCommand::Climb:
		Say(WorldContext, TEXT("Popping up."), 2.2f);
		break;
	case ESkyguardPilotCommand::Descend:
		Say(WorldContext, TEXT("Dropping behind cover."), 2.2f);
		break;
	case ESkyguardPilotCommand::FaceTarget:
		Say(WorldContext, TEXT("Coming onto your target."), 2.4f);
		break;
	case ESkyguardPilotCommand::Pursuit:
	default:
		Say(WorldContext, TEXT("Staying in the fight."), 2.2f);
		break;
	}
}

void SkyguardPilotVoice::WarnOffAxis(UObject* WorldContext)
{
	Say(WorldContext, TEXT("Break the glass — threat off your sensor."), 3.2f);
}

void SkyguardPilotVoice::CallLock(UObject* WorldContext)
{
	Say(WorldContext, TEXT("Good lock. Missile is yours."), 2.4f);
}

void SkyguardPilotVoice::CallReload(UObject* WorldContext, const TCHAR* Station)
{
	Say(
		WorldContext,
		*FString::Printf(TEXT("Reloading %s."), Station ? Station : TEXT("guns")),
		2.2f);
}

void SkyguardPilotVoice::CallEvent(
	UObject* WorldContext,
	const ESkyguardPilotLine Line)
{
	switch (Line)
	{
	case ESkyguardPilotLine::RadarLit:
		Say(WorldContext, TEXT("Radar just lit us. ADA is going to get faster."), 3.2f);
		break;
	case ESkyguardPilotLine::CargoHit:
		Say(WorldContext, TEXT("Cargo is taking hits. Prioritize the inbound."), 2.8f);
		break;
	case ESkyguardPilotLine::CargoCritical:
		Say(WorldContext, TEXT("That hull is on fire. We lose it, we lose the sortie."), 3.2f);
		break;
	case ESkyguardPilotLine::ShipRadarDown:
		Say(WorldContext, TEXT("Their search radar is down. Window is ours."), 2.8f);
		break;
	case ESkyguardPilotLine::ShipEnginesDown:
		Say(WorldContext, TEXT("Engines killed. She's dead in the water."), 2.8f);
		break;
	case ESkyguardPilotLine::ShipLauncherDown:
		Say(WorldContext, TEXT("Launcher cold. No more inbound from that hull."), 2.8f);
		break;
	case ESkyguardPilotLine::ShipCannonDown:
		Say(WorldContext, TEXT("Their cannon is scrap. Close if you want."), 2.6f);
		break;
	case ESkyguardPilotLine::ShipDeckDown:
		Say(WorldContext, TEXT("Drone deck is burning. No more rotors off that ship."), 2.8f);
		break;
	case ESkyguardPilotLine::ShipDead:
		Say(WorldContext, TEXT("Patrol ship is a hulk. Nice work."), 2.8f);
		break;
	case ESkyguardPilotLine::Inbound:
		Say(WorldContext, TEXT("Missile inbound — flares!"), 2.6f);
		break;
	case ESkyguardPilotLine::FlaresGood:
		Say(WorldContext, TEXT("Flares good. Break."), 2.0f);
		break;
	case ESkyguardPilotLine::Choice:
		Say(WorldContext, TEXT("Your call — kill that radar or stay on the ship."), 3.2f);
		break;
	case ESkyguardPilotLine::Extract:
		Say(WorldContext, TEXT("Extract. Get out of the glass."), 2.8f);
		break;
	case ESkyguardPilotLine::GoThermal:
		Say(WorldContext, TEXT("Blackout. Thermal. Don't hose the dark blocks."), 3.2f);
		break;
	case ESkyguardPilotLine::Win:
		Say(WorldContext, TEXT("We're Winchester-safe. Coming home."), 3.0f);
		break;
	case ESkyguardPilotLine::Fail:
		Say(WorldContext, TEXT("That's a loss. We go back in or we go home."), 3.0f);
		break;
	case ESkyguardPilotLine::LoadoutPrompt:
		Say(WorldContext, TEXT("Pick a loadout. One armor, two rockets, three intercept, four balanced."), 4.0f);
		break;
	default:
		break;
	}
}
