#include "SkyguardRuntimeMeshCatalog.h"

#include "Engine/StaticMesh.h"
#include "UObject/SoftObjectPath.h"

DEFINE_LOG_CATEGORY_STATIC(LogSkyguardRuntimeMeshCatalog, Log, All);

const TCHAR* USkyguardRuntimeMeshCatalog::DefaultCatalogAssetPath =
	TEXT("/Game/Skyguard/Data/DA_SkyguardRuntimeMeshCatalog.DA_SkyguardRuntimeMeshCatalog");

namespace SkyguardRuntimeMeshCatalogPrivate
{
	FSkyguardMeshBindSlot MakeSlot(
		const TCHAR* SlotId,
		const TCHAR* PreferredPath,
		const TCHAR* ProxyFallbackPath,
		const TCHAR* Notes)
	{
		FSkyguardMeshBindSlot Slot;
		Slot.SlotId = FName(SlotId);
		if (PreferredPath && PreferredPath[0] != TEXT('\0'))
		{
			Slot.Preferred = TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(PreferredPath));
		}
		if (ProxyFallbackPath && ProxyFallbackPath[0] != TEXT('\0'))
		{
			Slot.ProxyFallback = TSoftObjectPtr<UStaticMesh>(
				FSoftObjectPath(ProxyFallbackPath));
		}
		Slot.Notes = Notes ? Notes : FString();
		return Slot;
	}

	UStaticMesh* TryLoadSoft(const TSoftObjectPtr<UStaticMesh>& SoftMesh)
	{
		if (SoftMesh.IsNull())
		{
			return nullptr;
		}
		if (UStaticMesh* Loaded = SoftMesh.Get())
		{
			return Loaded;
		}
		return SoftMesh.LoadSynchronous();
	}

	UStaticMesh* TryLoadPath(const FSoftObjectPath& Path)
	{
		if (!Path.IsValid())
		{
			return nullptr;
		}
		return Cast<UStaticMesh>(Path.TryLoad());
	}
}

void USkyguardRuntimeMeshCatalog::EnsureDefaultSlots()
{
	const TArray<FSkyguardMeshBindSlot>& Defaults = GetCodeDefaultSlots();
	for (const FSkyguardMeshBindSlot& DefaultSlot : Defaults)
	{
		if (FindSlot(DefaultSlot.SlotId))
		{
			continue;
		}
		Slots.Add(DefaultSlot);
	}
}

const FSkyguardMeshBindSlot* USkyguardRuntimeMeshCatalog::FindSlot(
	const FName SlotId) const
{
	return Slots.FindByPredicate([SlotId](const FSkyguardMeshBindSlot& Slot)
	{
		return Slot.SlotId == SlotId;
	});
}

UStaticMesh* USkyguardRuntimeMeshCatalog::ResolveMesh(const FName SlotId) const
{
	if (const FSkyguardMeshBindSlot* Slot = FindSlot(SlotId))
	{
		return ResolveSlot(*Slot);
	}
	return ResolveDefaultSlot(SlotId);
}

UStaticMesh* USkyguardRuntimeMeshCatalog::ResolveSlot(
	const FSkyguardMeshBindSlot& Slot)
{
	using namespace SkyguardRuntimeMeshCatalogPrivate;

	if (UStaticMesh* Preferred = TryLoadSoft(Slot.Preferred))
	{
		return Preferred;
	}
	if (UStaticMesh* Proxy = TryLoadSoft(Slot.ProxyFallback))
	{
		return Proxy;
	}

	const FSoftObjectPath WebGamePath = GetWebGameLastResortPath(Slot.SlotId);
	if (UStaticMesh* WebGame = TryLoadPath(WebGamePath))
	{
		LogWebGameLastResortOnce(Slot.SlotId);
		return WebGame;
	}
	return nullptr;
}

UStaticMesh* USkyguardRuntimeMeshCatalog::ResolveDefaultSlot(const FName SlotId)
{
	for (const FSkyguardMeshBindSlot& Slot : GetCodeDefaultSlots())
	{
		if (Slot.SlotId == SlotId)
		{
			return ResolveSlot(Slot);
		}
	}
	return nullptr;
}

UStaticMesh* USkyguardRuntimeMeshCatalog::ResolveOrderedSoftPaths(
	const TArray<FSoftObjectPath>& OrderedPaths,
	const FName SlotIdForLastResortLog)
{
	using namespace SkyguardRuntimeMeshCatalogPrivate;

	for (const FSoftObjectPath& Path : OrderedPaths)
	{
		if (UStaticMesh* Mesh = TryLoadPath(Path))
		{
			return Mesh;
		}
	}

	if (!SlotIdForLastResortLog.IsNone())
	{
		const FSoftObjectPath WebGamePath =
			GetWebGameLastResortPath(SlotIdForLastResortLog);
		if (UStaticMesh* WebGame = TryLoadPath(WebGamePath))
		{
			LogWebGameLastResortOnce(SlotIdForLastResortLog);
			return WebGame;
		}
	}
	return nullptr;
}

const TArray<FSkyguardMeshBindSlot>& USkyguardRuntimeMeshCatalog::GetCodeDefaultSlots()
{
	using namespace SkyguardRuntimeMeshCatalogPrivate;

	// Preferred stays empty (or L88 for Yak) so WebGame is never Preferred.
	// ProxyFallback points at current Hero proxies. Accepting Codex / Blender
	// art updates Preferred only via manifest revision — never silent overwrite.
	static const TArray<FSkyguardMeshBindSlot> Defaults = {
		MakeSlot(
			TEXT("Gunner.Rifle"),
			TEXT(""),
			TEXT("/Game/Skyguard/Meshes/Hero/rifle_ads_proxy.rifle_ads_proxy"),
			TEXT("Preferred empty until accepted rifle art is staged. ProxyFallback=Hero ADS proxy.")),
		MakeSlot(
			TEXT("Gunner.Hand"),
			TEXT(""),
			TEXT("/Game/Skyguard/Meshes/Hero/glove_hand_proxy.glove_hand_proxy"),
			TEXT("Preferred empty until accepted glove art is staged.")),
		MakeSlot(
			TEXT("Gunner.Forearm"),
			TEXT(""),
			TEXT("/Game/Skyguard/Meshes/Hero/glove_arm_proxy.glove_arm_proxy"),
			TEXT("Preferred empty until accepted forearm art is staged.")),
		MakeSlot(
			TEXT("Gunner.Igla"),
			TEXT(""),
			TEXT("/Game/Skyguard/Meshes/Hero/igla_proxy.igla_proxy"),
			TEXT("Preferred empty until accepted Igla tube art is staged.")),
		MakeSlot(
			TEXT("Gunner.Cockpit"),
			TEXT(""),
			TEXT("/Game/Skyguard/Candidates/Apache/CPG_OpenVisor01/apache_cpg_open_visor/StaticMeshes/SM_ApacheCPG_OpenVisor.SM_ApacheCPG_OpenVisor"),
			TEXT("Open CPG visor candidate. No glass/cabin wall. Not accepted hero art. ProxyFallback only.")),
		MakeSlot(
			TEXT("Drone.Body"),
			TEXT(""),
			TEXT("/Game/Skyguard/Meshes/Hero/shahed_proxy.shahed_proxy"),
			TEXT("Preferred empty until accepted Shahed body is staged. Prefer Hero over WebGame.")),
		MakeSlot(
			TEXT("Drone.HeavyBody"),
			TEXT(""),
			TEXT("/Game/Skyguard/Meshes/Hero/shahed_heavy_proxy.shahed_heavy_proxy"),
			TEXT("Preferred empty until accepted heavy Shahed body is staged.")),
		MakeSlot(
			TEXT("Vehicle.Truck"),
			TEXT(""),
			TEXT("/Game/Skyguard/Meshes/Hero/radar_truck_proxy.radar_truck_proxy"),
			TEXT("Preferred empty until accepted truck art is staged. ProxyFallback=Hero radar truck.")),
		MakeSlot(
			TEXT("Vehicle.Car"),
			TEXT(""),
			TEXT("/Game/Skyguard/Meshes/Hero/city_car_proxy.city_car_proxy"),
			TEXT("Preferred empty until accepted car art is staged. ProxyFallback=Hero city car.")),
		MakeSlot(
			TEXT("Vehicle.Bus"),
			TEXT(""),
			TEXT("/Game/Skyguard/Meshes/Hero/city_bus_proxy.city_bus_proxy"),
			TEXT("Preferred empty until accepted bus art is staged. ProxyFallback=Hero city bus.")),
		MakeSlot(
			TEXT("Apache.Airframe"),
			TEXT(""),
			TEXT("/Game/Skyguard/Candidates/Apache/Airframe_Silhouette01/apache_airframe_open_cpg/StaticMeshes/SM_ApacheAirframe_Silhouette.SM_ApacheAirframe_Silhouette"),
			TEXT("Open-CPG silhouette candidate. Not accepted hero art. ProxyFallback only.")),
		MakeSlot(
			TEXT("Yak.Airframe"),
			TEXT("/Game/Skyguard/Meshes/L88/yak52_l88_silhouette_blockout/StaticMeshes/GEO_Airframe.GEO_Airframe"),
			TEXT("/Game/Skyguard/Meshes/Hero/yak52_proxy.yak52_proxy"),
			TEXT("L88 Preferred when present; ProxyFallback=Hero yak52_proxy (yak52_hd_proxy secondary in ConfigureVisual).")),
	};
	return Defaults;
}

FSoftObjectPath USkyguardRuntimeMeshCatalog::GetWebGameLastResortPath(
	const FName SlotId)
{
	if (SlotId == TEXT("Gunner.Rifle"))
	{
		return FSoftObjectPath(
			TEXT("/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-fde.rifle-fde"));
	}
	if (SlotId == TEXT("Gunner.Hand"))
	{
		return FSoftObjectPath(
			TEXT("/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-glove.rifle-glove"));
	}
	if (SlotId == TEXT("Gunner.Forearm"))
	{
		return FSoftObjectPath(
			TEXT("/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-sleeve.rifle-sleeve"));
	}
	if (SlotId == TEXT("Gunner.Igla"))
	{
		return FSoftObjectPath(
			TEXT("/Game/Skyguard/Meshes/WebGame/skyguard-interceptor/StaticMeshes/compact-launcher-tube.compact-launcher-tube"));
	}
	if (SlotId == TEXT("Drone.Body") || SlotId == TEXT("Drone.HeavyBody"))
	{
		return FSoftObjectPath(
			TEXT("/Game/Skyguard/Meshes/WebGame/skyguard-drone/StaticMeshes/drone-body.drone-body"));
	}
	return FSoftObjectPath();
}

void USkyguardRuntimeMeshCatalog::LogWebGameLastResortOnce(const FName SlotId)
{
	static TSet<FName> LoggedSlots;
	if (LoggedSlots.Contains(SlotId))
	{
		return;
	}
	LoggedSlots.Add(SlotId);
	UE_LOG(
		LogSkyguardRuntimeMeshCatalog,
		Warning,
		TEXT("Mesh bind slot '%s' fell back to WebGame last-resort (Preferred and ProxyFallback missing)."),
		*SlotId.ToString());
}
