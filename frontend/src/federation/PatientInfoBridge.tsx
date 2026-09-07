/**
 * Framework-agnostic mount for PatientInfo (see bridgeClient.ts).
 *
 *     const provider = await loadRemote("labs_results_remote/PatientInfoBridge");
 *     await provider().render({ dom, baseUrl, getToken, ... });
 *     provider().destroy({ moduleName, dom });
 *
 * `./PatientInfo` is unchanged, so React hosts such as ht-phr are unaffected.
 */
import { useMemo } from "react";
import { createBridgeComponent } from "@module-federation/bridge-react/v19";

import PatientInfo from "./PatientInfo";
import type { PatientInfoProps } from "./patientInfoTypes";
import { buildBridgeClient, type BridgeConnectionProps } from "./bridgeClient";

export interface PatientInfoBridgeProps
  extends Omit<PatientInfoProps, "apiClient" | "queryClient" | "apiBasePath">,
    BridgeConnectionProps {}

function PatientInfoBridgeRoot({
  baseUrl,
  apiBasePath = "/api",
  getToken,
  ...rest
}: PatientInfoBridgeProps) {
  const apiClient = useMemo(
    () => buildBridgeClient(baseUrl, apiBasePath, getToken),
    [baseUrl, apiBasePath, getToken],
  );

  // apiBasePath is already baked into the client's baseURL, so the component
  // must not prefix request paths with it a second time.
  return <PatientInfo apiClient={apiClient} apiBasePath="" {...rest} />;
}

export default createBridgeComponent({ rootComponent: PatientInfoBridgeRoot });
