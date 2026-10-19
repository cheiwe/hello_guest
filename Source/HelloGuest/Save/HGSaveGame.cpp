#include "Save/HGSaveGame.h"

void UHGSaveGame::Migrate()
{
	// No older layouts exist yet. When LatestVersion is bumped, convert old fields here.
	Version = LatestVersion;
}
