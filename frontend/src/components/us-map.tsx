'use client';

import { useEffect, useRef, useState, useCallback, memo } from 'react';
import { createPortal } from 'react-dom';
import { useRouter } from 'next/navigation';
import {
  ComposableMap,
  Geographies,
  Geography,
  ZoomableGroup,
} from 'react-simple-maps';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { X } from 'lucide-react';

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
  /** @deprecated Use selectedStates + onToggleState for multi-select behavior */
  onStateSelect?: (stateAbbr: string) => void;
  /** Array of currently selected state abbreviations (e.g., ['VA', 'NC']) */
  selectedStates?: string[];
  /** Toggle handler for multi-select mode */
  onToggleState?: (stateAbbr: string) => void;
}

interface GeoType {
  rsmKey: string;
  id: string;
  properties: { name: string };
  geometry: object;
}

function MapGeographies({
  onLoaded,
  onMouseEnter,
  onMouseLeave,
  onSelectState,
  geographies,
  selectedStates = [],
}: {
  onLoaded: () => void;
  onMouseEnter: (geo: GeoType, event: React.MouseEvent) => void;
  onMouseLeave: () => void;
  onSelectState: (stateAbbr: string) => void;
  geographies: GeoType[];
  selectedStates?: string[];
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
    const isSelected = stateAbbr && selectedStates.includes(stateAbbr);

    return (
      <Geography
        key={geo.rsmKey}
        geography={geo}
        onMouseEnter={(event: React.MouseEvent) => onMouseEnter(geo, event)}
        onMouseLeave={onMouseLeave}
        onClick={() => stateAbbr && onSelectState(stateAbbr)}
        tabIndex={0}
        onKeyDown={(event: React.KeyboardEvent) => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            if (stateAbbr) {
              onSelectState(stateAbbr);
            }
          }
        }}
        aria-label={stateAbbr ? `${STATE_NAMES[stateAbbr]}${isSelected ? ' (selected)' : ''}` : 'Unknown state'}
        aria-pressed={isSelected}
        role="button"
        style={{
          default: {
            fill: isSelected ? 'hsl(45, 70%, 47%)' : 'hsl(222, 60%, 15%)',
            stroke: isSelected ? 'hsl(45, 70%, 35%)' : 'hsl(220, 15%, 70%)',
            strokeWidth: isSelected ? 1 : 0.5,
            outline: 'none',
            cursor: 'pointer',
            transition: 'fill 0.2s ease, stroke 0.2s ease, stroke-width 0.2s ease',
          },
          hover: {
            fill: isSelected ? 'hsl(45, 70%, 55%)' : 'hsl(45, 70%, 47%)',
            stroke: 'hsl(45, 70%, 35%)',
            strokeWidth: 1,
            outline: 'none',
            cursor: 'pointer',
          },
          pressed: {
            fill: 'hsl(45, 70%, 40%)',
            stroke: 'hsl(45, 70%, 30%)',
            strokeWidth: 1,
            outline: 'none',
          },
        }}
      />
    );
  });
}

function USMapComponent({
  className = '',
  onStateSelect,
  selectedStates = [],
  onToggleState
}: USMapProps) {
  const router = useRouter();
  const [hoveredState, setHoveredState] = useState<TooltipState | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const handleStateClick = useCallback(
    (stateAbbr: string) => {
      // Multi-select mode: use toggle handler
      if (onToggleState) {
        onToggleState(stateAbbr);
      }
      // Legacy mode: use onStateSelect or navigate
      else if (onStateSelect) {
        onStateSelect(stateAbbr);
      } else {
        router.push(`/search?state=${stateAbbr}`);
      }
    },
    [router, onStateSelect, onToggleState]
  );

  const handleDropdownChange = useCallback(
    (value: string) => {
      handleStateClick(value);
    },
    [handleStateClick]
  );

  const handleMouseEnter = useCallback(
    (geo: GeoType, event: React.MouseEvent) => {
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

  const handleMouseMove = useCallback(
    (event: React.MouseEvent) => {
      if (hoveredState) {
        setHoveredState((prev) =>
          prev ? { ...prev, x: event.clientX, y: event.clientY } : null
        );
      }
    },
    [hoveredState]
  );

  const handleMouseLeave = useCallback(() => {
    setHoveredState(null);
  }, []);

  return (
    <div className={`relative ${className}`}>
      {/* Mobile: Dropdown Select with Selected Chips */}
      <div className="md:hidden space-y-3">
        {/* Selected states as removable chips */}
        {selectedStates.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {selectedStates.map((abbr) => (
              <button
                key={abbr}
                type="button"
                onClick={() => handleStateClick(abbr)}
                className="inline-flex items-center gap-1.5 rounded-full bg-[hsl(45,70%,47%)] px-3 py-1.5 text-sm font-medium text-[hsl(222,60%,15%)] transition-colors hover:bg-[hsl(45,70%,55%)]"
                aria-label={`Remove ${STATE_NAMES[abbr] || abbr}`}
              >
                {STATE_NAMES[abbr] || abbr}
                <X className="h-3.5 w-3.5" />
              </button>
            ))}
            {selectedStates.length > 1 && (
              <button
                type="button"
                onClick={() => {
                  // Clear all selected states
                  selectedStates.forEach((abbr) => handleStateClick(abbr));
                }}
                className="inline-flex items-center gap-1 rounded-full border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-800"
              >
                Clear all
              </button>
            )}
          </div>
        )}

        {/* Dropdown to add states */}
        <Select onValueChange={handleDropdownChange} value={undefined}>
          <SelectTrigger className="w-full border-[hsl(var(--v4v-navy)/0.3)] bg-white text-gray-700">
            <SelectValue placeholder={selectedStates.length > 0 ? "Add another state" : "Select a state to explore resources"} />
          </SelectTrigger>
          <SelectContent className="max-h-[300px]">
            {STATES_LIST.map(([abbr, name]) => {
              const isSelected = selectedStates.includes(abbr);
              return (
                <SelectItem
                  key={abbr}
                  value={abbr}
                  className={isSelected ? 'bg-[hsl(45,70%,47%)/0.2]' : ''}
                >
                  <span className="flex items-center gap-2">
                    {name}
                    {isSelected && <span className="text-xs text-muted-foreground">(selected)</span>}
                  </span>
                </SelectItem>
              );
            })}
          </SelectContent>
        </Select>
      </div>

      {/* Desktop: Interactive Map */}
      <div className="hidden md:block" onMouseMove={handleMouseMove}>
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
                  selectedStates={selectedStates}
                />
              )}
            </Geographies>
          </ZoomableGroup>
        </ComposableMap>

      </div>

      {/* Tooltip - rendered via portal to bypass any transform issues */}
      {hoveredState && typeof document !== 'undefined' && createPortal(
        <div
          className="pointer-events-none fixed z-[9999] rounded-md bg-[hsl(var(--v4v-navy))] px-3 py-1.5 text-sm font-medium text-white shadow-lg"
          style={{
            left: hoveredState.x,
            top: hoveredState.y - 40,
            transform: 'translateX(-50%)',
          }}
        >
          {hoveredState.name}
        </div>,
        document.body
      )}

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

      {/* DC & Territories - not clickable on the map */}
      <div className="mt-4 flex flex-col items-center gap-2">
        <span className="text-xs text-[hsl(var(--muted-foreground))]">DC & Territories</span>
        <div className="flex flex-wrap justify-center gap-2">
          {[
            { abbr: 'DC', name: 'DC' },
            { abbr: 'PR', name: 'Puerto Rico' },
            { abbr: 'GU', name: 'Guam' },
            { abbr: 'VI', name: 'Virgin Islands' },
            { abbr: 'AS', name: 'American Samoa' },
            { abbr: 'MP', name: 'Mariana Islands' },
          ].map(({ abbr, name }) => {
            const isSelected = selectedStates.includes(abbr);
            return (
              <button
                key={abbr}
                type="button"
                onClick={() => handleStateClick(abbr)}
                className={`
                  rounded-full px-3 py-1 text-xs font-medium transition-all duration-200
                  ${isSelected
                    ? 'bg-[hsl(45,70%,47%)] text-[hsl(222,60%,15%)] border border-[hsl(45,70%,35%)]'
                    : 'bg-[hsl(222,60%,15%)] text-white/80 border border-[hsl(220,15%,70%)] hover:bg-[hsl(45,70%,47%)] hover:text-[hsl(222,60%,15%)] hover:border-[hsl(45,70%,35%)]'
                  }
                `}
                aria-pressed={isSelected}
              >
                {name}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export const USMap = memo(USMapComponent);
export default USMap;
