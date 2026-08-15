#include "SkyguardMissionDirectorPresentationHelpers.h"

#include "SkyguardGunner.h"
#include "SkyguardSortieHudHostComponent.h"
#include "SkyguardSortiePresentationComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"

namespace SkyguardMissionDirectorPresentationHelpers
{
	void BindHudHostToPresentation(
		UObject* WorldContextObject,
		USkyguardSortiePresentationComponent* Presentation)
	{
		if (!WorldContextObject || !Presentation || !GEngine)
		{
			return;
		}

		UWorld* World = GEngine->GetWorldFromContextObject(
			WorldContextObject,
			EGetWorldErrorMode::ReturnNull);
		if (!World)
		{
			return;
		}

		AActor* HostOwner = World->GetFirstPlayerController();
		if (!HostOwner)
		{
			for (TActorIterator<ASkyguardGunner> It(World); It; ++It)
			{
				if (IsValid(*It))
				{
					HostOwner = *It;
					break;
				}
			}
		}
		if (!HostOwner)
		{
			return;
		}

		USkyguardSortieHudHostComponent* HudHost =
			HostOwner->FindComponentByClass<USkyguardSortieHudHostComponent>();
		if (!HudHost)
		{
			HudHost = NewObject<USkyguardSortieHudHostComponent>(
				HostOwner,
				TEXT("SortieHudHost"));
			if (!HudHost)
			{
				return;
			}
			HostOwner->AddInstanceComponent(HudHost);
			HudHost->RegisterComponent();
		}

		HudHost->BindPresentation(Presentation);
	}
}
