import { useState } from "react";
import { getTeamLogo } from "../teamLogos";

interface TeamLogoProps {
  teamId: number;
  teamName: string;
  season: string;
}

export default function TeamLogo({ teamId, teamName, season }: TeamLogoProps) {
  const logo = getTeamLogo(teamId, season, teamName);
  const [imageFailed, setImageFailed] = useState(false);

  if (!logo.src || imageFailed) {
    return (
      <span
        className="team-logo-fallback"
        title={`${teamName} logo unavailable`}
        aria-label={`${teamName} logo unavailable`}
      >
        —
      </span>
    );
  }

  return (
    <img
      className="team-logo"
      src={logo.src}
      alt={logo.alt}
      onError={() => setImageFailed(true)}
    />
  );
}

export function testTeamLogoLookup() {
  const testCases = [
    { teamId: 1610612747, season: "2025-26", name: "Los Angeles Lakers" },
    { teamId: 1610612747, season: "2024-25", name: "Los Angeles Lakers" },
    { teamId: 1610612747, season: "1996-97", name: "Los Angeles Lakers" },
    { teamId: 1610612744, season: "1979-80", name: "Golden State Warriors" },
    { teamId: 1610612744, season: "2025-26", name: "Golden State Warriors" },
  ];

  return testCases.map((testCase) => ({
    ...testCase,
    result: getTeamLogo(testCase.teamId, testCase.season, testCase.name).src,
  }));
}
