/**
 * Framework-agnostic mount for LabResults (see bridgeClient.ts).
 * `./LabResults` is unchanged, so React hosts such as ht-phr are unaffected.
 */
import { useMemo } from "react";
import { createBridgeComponent } from "@module-federation/bridge-react/v19";

import LabResults from "./LabResults";
import type { LabResultsProps } from "./types";
import { buildBridgeClient, type BridgeConnectionProps } from "./bridgeClient";

export interface LabResultsBridgeProps
  extends Omit<LabResultsProps, "apiClient" | "queryClient" | "apiBasePath">,
    BridgeConnectionProps {}

function LabResultsBridgeRoot({
  baseUrl,
  apiBasePath = "/api",
  getToken,
  ...rest
}: LabResultsBridgeProps) {
  const apiClient = useMemo(
    () => buildBridgeClient(baseUrl, apiBasePath, getToken),
    [baseUrl, apiBasePath, getToken],
  );

  return <LabResults apiClient={apiClient} apiBasePath="" {...rest} />;
}

export default createBridgeComponent({ rootComponent: LabResultsBridgeRoot });
