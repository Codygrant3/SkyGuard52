#include "SkyguardCpgDebrief.h"

#include "SkyguardCampaignRoster.h"
#include "SkyguardGunner.h"
#include "SkyguardGunshipSortieDirector.h"
#include "SkyguardPatrolShipBoss.h"
#include "SkyguardProtectAsset.h"
#include "SkyguardRadarNode.h"

namespace
{
	const TCHAR* MedalName(const int32 Medal)
	{
		if (Medal >= 3)
		{
			return TEXT("Gold");
		}
		if (Medal == 2)
		{
			return TEXT("Silver");
		}
		if (Medal == 1)
		{
			return TEXT("Bronze");
		}
		return TEXT("None");
	}

	const TCHAR* SystemLongName(const ESkyguardPatrolShipSystem System)
	{
		switch (System)
		{
		case ESkyguardPatrolShipSystem::Radar:
			return TEXT("Search Radar");
		case ESkyguardPatrolShipSystem::Cannon:
			return TEXT("Cannon");
		case ESkyguardPatrolShipSystem::Launcher:
			return TEXT("Launcher");
		case ESkyguardPatrolShipSystem::Engines:
			return TEXT("Engines");
		case ESkyguardPatrolShipSystem::DroneDeck:
			return TEXT("Drone Deck");
		default:
			return TEXT("System");
		}
	}

	void CollectDestroyedSystems(
		const ASkyguardPatrolShipBoss* Ship,
		TArray<ESkyguardPatrolShipSystem>& OutSystems)
	{
		OutSystems.Reset();
		if (!Ship)
		{
			return;
		}
		const ESkyguardPatrolShipSystem Systems[] = {
			ESkyguardPatrolShipSystem::Radar,
			ESkyguardPatrolShipSystem::Cannon,
			ESkyguardPatrolShipSystem::Launcher,
			ESkyguardPatrolShipSystem::Engines,
			ESkyguardPatrolShipSystem::DroneDeck
		};
		for (const ESkyguardPatrolShipSystem System : Systems)
		{
			if (Ship->IsSystemDead(System))
			{
				OutSystems.Add(System);
			}
		}
	}
}

FSkyguardCpgDebriefSnapshot SkyguardCaptureCpgDebrief(
	const ASkyguardGunshipSortieDirector* Director,
	const ASkyguardGunner* Gunner,
	const ASkyguardPatrolShipBoss* Ship)
{
	FSkyguardCpgDebriefSnapshot Snap;
	Snap.bValid = true;
	if (Director)
	{
		Snap.bWon = Director->GetBeat() == ESkyguardSortieBeat::Succeeded;
		Snap.MissionTitle = Director->GetMissionTitle();
		Snap.Score = Director->GetLastScore();
		Snap.Medal = Director->GetLastMedal();
		Snap.SelectedLoadout = Director->GetPendingLoadout();
		const FSkyguardCampaignMissionSpec& Spec =
			SkyguardCampaignRoster::Get(Director->GetMissionIndex());
		Snap.OutcomeNarrative = Snap.bWon ? Spec.Success : Spec.Failure;
		if (const ASkyguardProtectAsset* Cargo = Director->GetCargoAsset())
		{
			Snap.CargoPercent = FMath::RoundToInt(
				Cargo->GetIntegrityFraction() * 100.f);
		}
		if (const ASkyguardRadarNode* Radar = Director->GetRadarNode())
		{
			Snap.bRadarDead = Radar->IsDestroyed();
		}
		if (!Ship)
		{
			Ship = Director->GetPatrolShip();
		}
	}
	if (Gunner)
	{
		Snap.ShotsFired = Gunner->GetSortieShotsFired();
		Snap.Hits = Gunner->GetSortieHits();
		Snap.CannonReady = Gunner->GetCannonMagazine();
		Snap.RocketReady = Gunner->GetRocketAmmo();
		Snap.GuidedReady = Gunner->GetGuidedAmmo();
		if (!Director)
		{
			Snap.SelectedLoadout = Gunner->GetActiveLoadout();
		}
	}
	CollectDestroyedSystems(Ship, Snap.DestroyedSystems);
	if (Snap.MissionTitle.IsEmpty())
	{
		Snap.MissionTitle = TEXT("Sortie");
	}
	return Snap;
}

FString SkyguardBuildCpgDebriefCopy(const FSkyguardCpgDebriefSnapshot& Snap)
{
	FString SystemsLine;
	if (Snap.DestroyedSystems.Num() == 0)
	{
		SystemsLine = TEXT("none");
	}
	else
	{
		for (int32 Index = 0; Index < Snap.DestroyedSystems.Num(); ++Index)
		{
			if (Index > 0)
			{
				SystemsLine += TEXT(", ");
			}
			SystemsLine += SystemLongName(Snap.DestroyedSystems[Index]);
		}
	}

	const FSkyguardLoadoutSpec Spec = SkyguardResolveLoadout(Snap.SelectedLoadout);
	return FString::Printf(
		TEXT("%s — %s\n%s\nCPG combat: %d fired  %d hits  (30 mm · Hydra · Hellfire)\nStations: M230 %d  HYDRA %d  HLF %d\nCargo %d%%   Score %d   Medal %s\nPatrol ship systems stripped: %s\nLoadout 1-4: Anti-Armor  Rocket Heavy  Intercept  Balanced\nCurrent: %s — %s\nN / Enter continues"),
		*Snap.MissionTitle,
		Snap.bWon ? TEXT("WIN") : TEXT("FAIL"),
		*Snap.OutcomeNarrative,
		Snap.ShotsFired,
		Snap.Hits,
		Snap.CannonReady,
		Snap.RocketReady,
		Snap.GuidedReady,
		Snap.CargoPercent,
		Snap.Score,
		MedalName(Snap.Medal),
		*SystemsLine,
		SkyguardLoadoutDisplayName(Snap.SelectedLoadout),
		Spec.PlaystyleLine);
}
