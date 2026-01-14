declare module 'react-simple-maps' {
  import { ComponentType, CSSProperties, ReactNode } from 'react';

  interface ProjectionConfig {
    scale?: number;
    center?: [number, number];
    rotate?: [number, number, number];
    parallels?: [number, number];
  }

  interface ComposableMapProps {
    projection?: string;
    projectionConfig?: ProjectionConfig;
    width?: number;
    height?: number;
    className?: string;
    style?: CSSProperties;
    children?: ReactNode;
  }

  interface ZoomableGroupProps {
    center?: [number, number];
    zoom?: number;
    minZoom?: number;
    maxZoom?: number;
    translateExtent?: [[number, number], [number, number]];
    onMoveStart?: (position: { x: number; y: number; k: number }) => void;
    onMove?: (position: { x: number; y: number; k: number }) => void;
    onMoveEnd?: (position: { x: number; y: number; k: number }) => void;
    filterZoomEvent?: (event: Event) => boolean;
    children?: ReactNode;
  }

  interface GeographiesProps {
    geography: string | object;
    children: (data: { geographies: GeographyObject[] }) => ReactNode;
  }

  interface GeographyObject {
    id: string;
    rsmKey: string;
    properties: { name: string; [key: string]: unknown };
    geometry: object;
  }

  interface GeographyStyleProps {
    default?: CSSProperties;
    hover?: CSSProperties;
    pressed?: CSSProperties;
  }

  interface GeographyProps {
    geography: GeographyObject;
    style?: GeographyStyleProps;
    onMouseEnter?: (event: React.MouseEvent) => void;
    onMouseLeave?: (event: React.MouseEvent) => void;
    onMouseDown?: (event: React.MouseEvent) => void;
    onMouseUp?: (event: React.MouseEvent) => void;
    onClick?: (event: React.MouseEvent) => void;
    onFocus?: (event: React.FocusEvent) => void;
    onBlur?: (event: React.FocusEvent) => void;
    onKeyDown?: (event: React.KeyboardEvent) => void;
    tabIndex?: number;
    'aria-label'?: string;
    role?: string;
    className?: string;
  }

  interface MarkerProps {
    coordinates: [number, number];
    children?: ReactNode;
    style?: GeographyStyleProps;
    onMouseEnter?: (event: React.MouseEvent) => void;
    onMouseLeave?: (event: React.MouseEvent) => void;
    onClick?: (event: React.MouseEvent) => void;
  }

  interface LineProps {
    from: [number, number];
    to: [number, number];
    coordinates?: [number, number][];
    stroke?: string;
    strokeWidth?: number;
    strokeLinecap?: 'butt' | 'round' | 'square';
    strokeDasharray?: string;
    fill?: string;
    className?: string;
    style?: CSSProperties;
  }

  interface AnnotationProps {
    subject: [number, number];
    dx?: number;
    dy?: number;
    curve?: number;
    connectorProps?: object;
    children?: ReactNode;
  }

  interface GraticuleProps {
    stroke?: string;
    strokeWidth?: number;
    fill?: string;
    step?: [number, number];
    className?: string;
    style?: CSSProperties;
  }

  interface SphereProps {
    id?: string;
    stroke?: string;
    strokeWidth?: number;
    fill?: string;
    className?: string;
    style?: CSSProperties;
  }

  export const ComposableMap: ComponentType<ComposableMapProps>;
  export const ZoomableGroup: ComponentType<ZoomableGroupProps>;
  export const Geographies: ComponentType<GeographiesProps>;
  export const Geography: ComponentType<GeographyProps>;
  export const Marker: ComponentType<MarkerProps>;
  export const Line: ComponentType<LineProps>;
  export const Annotation: ComponentType<AnnotationProps>;
  export const Graticule: ComponentType<GraticuleProps>;
  export const Sphere: ComponentType<SphereProps>;
}
