'use client';

import { useEffect, useRef, useState, useCallback, memo } from 'react';
import { useRouter } from 'next/navigation';
import {
  ComposableMap,
  Geographies,
  Geography,
  type GeographyObject,
  ZoomableGroup,
} from 'react-simple-maps';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

const GEO_URL = 'https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json';

// State abbreviations mapped to FIPS codes
const STATE_FIPS_TO_ABBR: Record<string, string> = {
  '01': 'AL', '02': 'AK', '04': 'AZ', '05': 'AR', '06': 'CA',
  '08': 'CO', '09': 'CT', '10': 'DE', '11': 'DC', '12': 'FL',
  '13': 'GA', '15': 'HI', '16': 'ID', '17': 'IL', '18': 'IN',
  '19': 'IA', '20': 'KS', '21': 'KY', '22': 'LA', '23': 'ME',
  '24': 'MD', '25': 'MA', '26': 'MI', '27': 'MN', '28': 'MS',
  '29': 'MO', '30': 'MT', '31': 'NE', '32': 'NV', '33': 'NH',
  '34': 'NJ', '35': 'NM', '36': 'NY', '37': 'NC', '38': 'ND',
  '39': 'OH', '40': 'OK', '41': 'OR', '42': 'PA', '44': 'RI',
  '45': 'SC', '46': 'SD', '47': 'TN', '48': 'TX', '49': 'UT',
  '50': 'VT', '51': 'VA', '53': 'WA', '54': 'WV', '55': 'WI',
  '56': 'WY', '72': 'PR',
};

// Full state names for display and dropdown
const STATE_NAMES: Record<string, string> = {
  'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
  'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
  'DC': 'District of Columbia', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii',
  'AS': 'American Samoa', 'GU': 'Guam',
  'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
  'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine',
  'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota',
  'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska',
  'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico',
  'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
  'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island',
  'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas',
  'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington',
  'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming', 'PR': 'Puerto Rico',
  'MP': 'Northern Mariana Islands', 'VI': 'U.S. Virgin Islands',
};

// Sorted list of states for dropdown
const STATES_LIST = Object.entries(STATE_NAMES)
  .filter(([abbr]) => abbr !== 'DC') // DC is tiny on the map; keep it in list elsewhere
  .sort((a, b) => a[1].localeCompare(b[1]));

interface TooltipState {
  name: string;
  x: number;
  y: number;
}

interface USMapProps {
  className?: string;
  onStateSelect?: (stateAbbr: string) => void;
}

function MapGeographies({
  onLoaded,
  onMouseEnter,
  onMouseLeave,
  onSelectState,
  geographies,
}: {
  onLoaded: () => void;
  onMouseEnter: (geo: GeographyObject, event: React.MouseEvent) => void;
  onMouseLeave: () => void;
  onSelectState: (stateAbbr: string) => void;
  geographies: GeographyObject[];
}) {
  const didNotifyLoaded = useRef(false);

  useEffect(() => {
    if (didNotifyLoaded.current) return;
    if (geographies.length === 0) return;
    didNotifyLoaded.current = true;
    onLoaded();
  }, [geographies.length, onLoaded]);

  return geographies.map((geo) => {
    const stateAbbr = STATE_FIPS_TO_ABBR[geo.id];
    return (
      <Geography
        key={geo.rsmKey}
        geography={geo}
        onMouseEnter={(event) => onMouseEnter(geo, event)}
        onMouseLeave={onMouseLeave}
        onClick={() => stateAbbr && onSelectState(stateAbbr)}
        tabIndex={0}
        onKeyDown={(event) => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            if (stateAbbr) {
              onSelectState(stateAbbr);
            }
          }
        }}
        aria-label={stateAbbr ? STATE_NAMES[stateAbbr] : 'Unknown state'}
        role="button"
        style={{
          default: {
            fill: 'hsl(222, 60%, 15%)', // Slightly lighter navy for visibility
            stroke: 'hsl(220, 15%, 70%)', // Light border
            strokeWidth: 0.5,
            outline: 'none',
            cursor: 'pointer',
            transition: 'fill 0.2s ease',
          },
          hover: {
            fill: 'hsl(45, 70%, 47%)', // Gold on hover
            stroke: 'hsl(45, 70%, 35%)', // Darker gold border
            strokeWidth: 1,
            outline: 'none',
            cursor: 'pointer',
          },
          pressed: {
            fill: 'hsl(45, 70%, 40%)', // Darker gold when pressed
            stroke: 'hsl(45, 70%, 30%)',
            strokeWidth: 1,
            outline: 'none',
          },
        }}
      />
    );
  });
}

function USMapComponent({ className = '', onStateSelect }: USMapProps) {
  const router = useRouter();
  const [hoveredState, setHoveredState] = useState<TooltipState | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const handleStateClick = useCallback(
    (stateAbbr: string) => {
      if (onStateSelect) {
        onStateSelect(stateAbbr);
      } else {
        router.push(`/search?state=${stateAbbr}`);
      }
    },
    [router, onStateSelect]
  );

  const handleDropdownChange = useCallback(
    (value: string) => {
      handleStateClick(value);
    },
    [handleStateClick]
  );

  const handleMouseEnter = useCallback(
    (geo: { id: string; properties: { name: string } }, event: React.MouseEvent) => {
      const stateAbbr = STATE_FIPS_TO_ABBR[geo.id];
      const stateName = stateAbbr ? STATE_NAMES[stateAbbr] : geo.properties.name;

      setHoveredState({
        name: stateName || 'Unknown',
        x: event.clientX,
        y: event.clientY,
      });
    },
    []
  );

  const handleMouseLeave = useCallback(() => {
    setHoveredState(null);
  }, []);

  return (
    <div className={`relative ${className}`}>
      {/* Mobile: Dropdown Select */}
      <div className="md:hidden">
        <Select onValueChange={handleDropdownChange}>
          <SelectTrigger className="w-full border-[hsl(var(--v4v-navy)/0.3)] bg-white">
            <SelectValue placeholder="Select a state to explore resources" />
          </SelectTrigger>
          <SelectContent className="max-h-[300px]">
            {STATES_LIST.map(([abbr, name]) => (
              <SelectItem key={abbr} value={abbr}>
                {name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Desktop: Interactive Map */}
      <div className="hidden md:block">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-[hsl(var(--v4v-cream))]">
            <div className="text-[hsl(var(--muted-foreground))]">Loading map...</div>
          </div>
        )}

        <ComposableMap
          projection="geoAlbersUsa"
          projectionConfig={{
            scale: 1000,
          }}
          className="w-full h-auto"
          style={{ maxHeight: '500px' }}
        >
          <ZoomableGroup center={[0, 0]} zoom={1}>
            <Geographies geography={GEO_URL}>
              {({ geographies }) => (
                <MapGeographies
                  geographies={geographies}
                  onLoaded={() => setIsLoading(false)}
                  onMouseEnter={handleMouseEnter}
                  onMouseLeave={handleMouseLeave}
                  onSelectState={handleStateClick}
                />
              )}
            </Geographies>
          </ZoomableGroup>
        </ComposableMap>

        {/* Tooltip */}
        {hoveredState && (
          <div
            className="pointer-events-none fixed z-50 rounded-md bg-[hsl(var(--v4v-navy))] px-3 py-1.5 text-sm font-medium text-white shadow-lg"
            style={{
              left: hoveredState.x + 12,
              top: hoveredState.y - 30,
            }}
          >
            {hoveredState.name}
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="mt-4 flex items-center justify-center gap-4 text-xs text-[hsl(var(--muted-foreground))]">
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-sm bg-[hsl(222,60%,15%)]" />
          <span>Click a state</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-sm bg-[hsl(45,70%,47%)]" />
          <span>Selected</span>
        </div>
      </div>
    </div>
  );
}

export const USMap = memo(USMapComponent);
export default USMap;
