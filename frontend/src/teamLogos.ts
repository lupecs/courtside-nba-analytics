export interface TeamLogoInfo {
  src: string | null;
  alt: string;
}

interface LogoEra {
  teamId: number;
  franchise: string;
  startSeason: number;
  endSeason: number | null;
  src: string;
}

const logoEras: LogoEra[] = [
  {
    teamId: 1610612750,
    franchise: "Minnesota Timberwolves",
    startSeason: 1996,
    endSeason: 2007,
    src: "/team-logos/historical/1996-97/1610612750.svg",
  },
  {
    teamId: 1610612765,
    franchise: "Detroit Pistons",
    startSeason: 1996,
    endSeason: 2000,
    src: "/team-logos/historical/1996-97/1610612765.svg",
  },
  {
    teamId: 1610612762,
    franchise: "Utah Jazz",
    startSeason: 1996,
    endSeason: 2003,
    src: "/team-logos/historical/1996-97/1610612762.svg",
  },
  {
    teamId: 1610612738,
    franchise: "Boston Celtics",
    startSeason: 1996,
    endSeason: 2024,
    src: "/team-logos/historical/1996-97/1610612738.svg",
  },
  {
    teamId: 1610612737,
    franchise: "Atlanta Hawks",
    startSeason: 1995,
    endSeason: 2006,
    src: "/team-logos/historical/1996-97/1610612737.svg",
  },
  {
    teamId: 1610612766,
    franchise: "Charlotte Hornets",
    startSeason: 1988,
    endSeason: 2001,
    src: "/team-logos/historical/1996-97/1610612766.svg",
  },
  {
    teamId: 1610612741,
    franchise: "Chicago Bulls",
    startSeason: 1966,
    endSeason: 2024,
    src: "/team-logos/historical/1996-97/1610612741.svg",
  },
  {
    teamId: 1610612739,
    franchise: "Cleveland Cavaliers",
    startSeason: 1994,
    endSeason: 2002,
    src: "/team-logos/historical/1996-97/1610612739.svg",
  },
  {
    teamId: 1610612742,
    franchise: "Dallas Mavericks",
    startSeason: 1993,
    endSeason: 2000,
    src: "/team-logos/historical/1996-97/1610612742.png",
  },
  {
    teamId: 1610612743,
    franchise: "Denver Nuggets",
    startSeason: 1993,
    endSeason: 2002,
    src: "/team-logos/historical/1996-97/1610612743.svg",
  },
  {
    teamId: 1610612744,
    franchise: "Golden State Warriors",
    startSeason: 1988,
    endSeason: 1996,
    src: "/team-logos/historical/1996-97/1610612744.png",
  },
  {
    teamId: 1610612745,
    franchise: "Houston Rockets",
    startSeason: 1995,
    endSeason: 2002,
    src: "/team-logos/historical/1996-97/1610612745.svg",
  },
  {
    teamId: 1610612754,
    franchise: "Indiana Pacers",
    startSeason: 1990,
    endSeason: 2004,
    src: "/team-logos/historical/1996-97/1610612754.svg",
  },
  {
    teamId: 1610612746,
    franchise: "Los Angeles Clippers",
    startSeason: 1984,
    endSeason: 2009,
    src: "/team-logos/historical/1996-97/1610612746.png",
  },
  {
    teamId: 1610612747,
    franchise: "Los Angeles Lakers",
    startSeason: 1975,
    endSeason: 1998,
    src: "/team-logos/historical/1996-97/1610612747.png",
  },
  {
    teamId: 1610612748,
    franchise: "Miami Heat",
    startSeason: 1988,
    endSeason: 1998,
    src: "/team-logos/historical/1996-97/1610612748.png",
  },
  {
    teamId: 1610612749,
    franchise: "Milwaukee Bucks",
    startSeason: 1993,
    endSeason: 2005,
    src: "/team-logos/historical/1996-97/1610612749.png",
  },
  {
    teamId: 1610612751,
    franchise: "New Jersey Nets",
    startSeason: 1990,
    endSeason: 1996,
    src: "/team-logos/historical/1996-97/1610612751.png",
  },
  {
    teamId: 1610612752,
    franchise: "New York Knicks",
    startSeason: 1995,
    endSeason: 2010,
    src: "/team-logos/historical/1996-97/1610612752.svg",
  },
  {
    teamId: 1610612753,
    franchise: "Orlando Magic",
    startSeason: 1989,
    endSeason: 1997,
    src: "/team-logos/historical/1996-97/1610612753.png",
  },
  {
    teamId: 1610612755,
    franchise: "Philadelphia 76ers",
    startSeason: 1977,
    endSeason: 1996,
    src: "/team-logos/historical/1996-97/1610612755.png",
  },
  {
    teamId: 1610612756,
    franchise: "Phoenix Suns",
    startSeason: 1992,
    endSeason: 1999,
    src: "/team-logos/historical/1996-97/1610612756.png",
  },
  {
    teamId: 1610612757,
    franchise: "Portland Trail Blazers",
    startSeason: 1990,
    endSeason: 2001,
    src: "/team-logos/historical/1996-97/1610612757.png",
  },
  {
    teamId: 1610612758,
    franchise: "Sacramento Kings",
    startSeason: 1994,
    endSeason: 2015,
    src: "/team-logos/historical/1996-97/1610612758.png",
  },
  {
    teamId: 1610612759,
    franchise: "San Antonio Spurs",
    startSeason: 1989,
    endSeason: 2001,
    src: "/team-logos/historical/1996-97/1610612759.png",
  },
  {
    teamId: 1610612760,
    franchise: "Seattle SuperSonics",
    startSeason: 1995,
    endSeason: 2000,
    src: "/team-logos/historical/1996-97/1610612760.png",
  },
  {
    teamId: 1610612761,
    franchise: "Toronto Raptors",
    startSeason: 1995,
    endSeason: 2007,
    src: "/team-logos/historical/1996-97/1610612761.png",
  },
  {
    teamId: 1610612761,
    franchise: "Toronto Raptors",
    startSeason: 1995,
    endSeason: 2007,
    src: "/team-logos/historical/1996-97/1610612761.png",
  },
  {
    teamId: 1610612763,
    franchise: "Vancouver Grizzlies",
    startSeason: 1995,
    endSeason: 2000,
    src: "/team-logos/historical/1996-97/1610612763.png",
  },
  {
  teamId: 1610612764,
  franchise: "Washington Bullets",
  startSeason: 1987,
  endSeason: 1996,
  src: "/team-logos/historical/1996-97/1610612764.png",
},
  // Current logo assets.
  // These are valid for the current 2025-26 season only
  // until their historical logo periods are verified.
  {
    teamId: 1610612737,
    franchise: "Atlanta Hawks",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612737.svg",
  },
  {
    teamId: 1610612738,
    franchise: "Boston Celtics",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612738.svg",
  },
  {
    teamId: 1610612751,
    franchise: "Brooklyn Nets",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612751.svg",
  },
  {
    teamId: 1610612766,
    franchise: "Charlotte Hornets",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612766.svg",
  },
  {
    teamId: 1610612741,
    franchise: "Chicago Bulls",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612741.svg",
  },
  {
    teamId: 1610612739,
    franchise: "Cleveland Cavaliers",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612739.svg",
  },
  {
    teamId: 1610612742,
    franchise: "Dallas Mavericks",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612742.svg",
  },
  {
    teamId: 1610612743,
    franchise: "Denver Nuggets",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612743.svg",
  },
  {
    teamId: 1610612765,
    franchise: "Detroit Pistons",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612765.svg",
  },
  {
    teamId: 1610612744,
    franchise: "Golden State Warriors",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612744.svg",
  },
  {
    teamId: 1610612745,
    franchise: "Houston Rockets",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612745.svg",
  },
  {
    teamId: 1610612754,
    franchise: "Indiana Pacers",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612754.svg",
  },
  {
    teamId: 1610612746,
    franchise: "LA Clippers",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612746.svg",
  },
  {
    teamId: 1610612747,
    franchise: "Los Angeles Lakers",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612747.svg",
  },
  {
    teamId: 1610612763,
    franchise: "Memphis Grizzlies",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612763.svg",
  },
  {
    teamId: 1610612748,
    franchise: "Miami Heat",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612748.svg",
  },
  {
    teamId: 1610612749,
    franchise: "Milwaukee Bucks",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612749.svg",
  },
  {
    teamId: 1610612750,
    franchise: "Minnesota Timberwolves",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612750.svg",
  },
  {
    teamId: 1610612740,
    franchise: "New Orleans Pelicans",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612740.svg",
  },
  {
    teamId: 1610612752,
    franchise: "New York Knicks",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612752.svg",
  },
  {
    teamId: 1610612760,
    franchise: "Oklahoma City Thunder",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612760.svg",
  },
  {
    teamId: 1610612753,
    franchise: "Orlando Magic",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612753.svg",
  },
  {
    teamId: 1610612755,
    franchise: "Philadelphia 76ers",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612755.svg",
  },
  {
    teamId: 1610612756,
    franchise: "Phoenix Suns",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612756.svg",
  },
  {
    teamId: 1610612757,
    franchise: "Portland Trail Blazers",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612757.svg",
  },
  {
    teamId: 1610612758,
    franchise: "Sacramento Kings",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612758.svg",
  },
  {
    teamId: 1610612759,
    franchise: "San Antonio Spurs",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612759.svg",
  },
  {
    teamId: 1610612761,
    franchise: "Toronto Raptors",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612761.svg",
  },
  {
    teamId: 1610612762,
    franchise: "Utah Jazz",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612762.svg",
  },
  {
    teamId: 1610612764,
    franchise: "Washington Wizards",
    startSeason: 2025,
    endSeason: null,
    src: "/team-logos/current/1610612764.svg",
  },
];

function getSeasonStartYear(season: string): number | null {
  const match = season.match(/^(\d{4})-\d{2}$/);
  return match ? Number(match[1]) : null;
}

export function getTeamLogo(
  teamId: number,
  season: string,
  teamName: string,
): TeamLogoInfo {
  const seasonYear = getSeasonStartYear(season);

  if (seasonYear === null) {
    return { src: null, alt: `${teamName} logo unavailable` };
  }

  const matchingLogo = logoEras.find(
    (logo) =>
      logo.teamId === teamId &&
      seasonYear >= logo.startSeason &&
      (logo.endSeason === null || seasonYear <= logo.endSeason),
  );

  if (!matchingLogo) {
    return { src: null, alt: `${teamName} logo unavailable` };
  }

  return {
    src: matchingLogo.src,
    alt: `${teamName} logo`,
  };
}
