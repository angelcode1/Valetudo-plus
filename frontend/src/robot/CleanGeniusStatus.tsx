import React from "react";
import {Alert, Box, Button, Chip, Divider, Typography} from "@mui/material";
import {Insights as CleanGeniusIcon} from "@mui/icons-material";
import {
    fetchX40CleanGeniusPreflight,
    X40CleanGeniusPreflight,
    useRobotInformationQuery,
    useX40CleanGeniusStatusQuery,
    X40CleanGeniusReadOnlyStatus,
    X40CleanGeniusSetting
} from "../api";
import DetailPageHeaderRow from "../components/DetailPageHeaderRow";
import PaperContainer from "../components/PaperContainer";

const DISPLAY_FIELDS: Array<{
    key: keyof X40CleanGeniusReadOnlyStatus["settings"];
    title: string;
    description: string;
}> = [
    {
        key: "cleanGenius",
        title: "CleanGenius setting",
        description: "Native SmartHost configuration. This is not a verified active cleaning mode."
    },
    {
        key: "autoReclean",
        title: "Auto Reclean setting",
        description: "Native SmartAutoMop setting. Negative values have unverified meanings."
    },
    {
        key: "autoRewash",
        title: "Auto Rewash setting",
        description: "Native SmartAutoWash setting; not a detected rewash event."
    },
    {
        key: "stainIdentification",
        title: "Stain handling setting",
        description: "Native StainIdentify value. The reference uses 1/2 for avoidance disabled/enabled; X40 behavior remains unverified."
    },
    {
        key: "hotWash",
        title: "Hot Wash setting",
        description: "Native HotWash configuration, not a measured water temperature."
    }
];

const STATE_LABELS: Record<X40CleanGeniusSetting["state"], string> = {
    off: "Off",
    on_setting: "On (setting)",
    mode_1_unverified: "Mode 1 (unverified)",
    mode_2_unverified: "Mode 2 (unverified)",
    unknown: "Unknown",
    unavailable: "Not reported"
};

const displaySetting = (setting: X40CleanGeniusSetting): string => {
    const label = STATE_LABELS[setting.state] ?? "Unknown";
    return setting.value === null ? label : `${label} (raw ${setting.value})`;
};

const CleanGeniusStatus = (): React.ReactElement => {
    const {
        data: robotInfo,
        isPending: robotInfoPending,
        isError: robotInfoError
    } = useRobotInformationQuery();

    const supported = robotInfo?.implementation === "DreameX40UltraValetudoRobot";

    const {
        data: status,
        isPending: statusPending,
        isFetching: statusFetching,
        isError: statusError,
        refetch
    } = useX40CleanGeniusStatusQuery(supported);

    const [fresh, setFresh] = React.useState<X40CleanGeniusPreflight | null>(null);
    const [freshBusy, setFreshBusy] = React.useState(false);
    const [freshError, setFreshError] = React.useState(false);
    const readFresh = async (): Promise<void> => {
        setFresh(null);
        setFreshError(false);
        setFreshBusy(true);
        try {
            setFresh(await fetchX40CleanGeniusPreflight());
        } catch {
            setFreshError(true);
        } finally {
            setFreshBusy(false);
        }
    };

    const policy = status?.valetudoPolicy === "experimental_controls_opted_in" ?
        "Experimental writable CleanGenius quirks are opted in. This page remains read-only." :
        status?.valetudoPolicy === "observe_only_preserve_smart_host" ?
            "Observe-only policy preserves the native SmartHost setting. Writable controls remain separately opted in." :
            "Valetudo normally disables positive SmartHost settings to protect manual controls. " +
        "A reported setting may not be the effective native cleaning mode.";

    return (
        <PaperContainer>
            <Box sx={{width: "100%"}}>
                <DetailPageHeaderRow
                    title="CleanGenius Status"
                    icon={<CleanGeniusIcon/>}
                    onRefreshClick={supported ? () => {
                        void refetch();
                    } : undefined}
                    isRefreshing={statusFetching}
                />

                <Box sx={{p: 2}}>
                    <Chip label="Read-only" variant="outlined" size="small"/>
                    <Typography variant="body2" color="textSecondary" sx={{mt: 1}}>
                        Cached native settings and an explicit fresh safety read are shown separately.
                        This page does not change settings or start cleaning.
                    </Typography>

                    {robotInfoPending && <Typography sx={{mt: 2}}>Checking robot model…</Typography>}
                    {robotInfoError && <Alert severity="error" sx={{mt: 2}}>Cannot determine the robot model.</Alert>}
                    {!robotInfoPending && !robotInfoError && !supported &&
                        <Alert severity="info" sx={{mt: 2}}>
                            CleanGenius status is available only for the Dreame X40 Ultra driver.
                        </Alert>
                    }

                    {supported && (
                        <>
                            <Box sx={{mt: 2, mb: 2}}>
                                <Button variant="outlined" disabled={freshBusy} onClick={() => {
                                    void readFresh();
                                }}>
                                    {freshBusy ? "Reading robot status…" : "Read fresh safety status"}
                                </Button>
                                <Typography variant="body2" sx={{mt: 1}}>
                                    Reads current mode, task, charging, error and dock status once. No setting is changed.
                                </Typography>
                                {freshError && <Alert severity="warning">Fresh status is unavailable. Idleness is not confirmed.</Alert>}
                                {fresh && (
                                    <Alert severity={fresh.activationAllowed ? "info" : "warning"} sx={{mt: 1}}>
                                        Mode {fresh.mode}, task {fresh.taskStatus}, charging {fresh.chargeCode},
                                        dock {fresh.dockWashCode}, error {fresh.errorClear ? "clear" : "not clear"}.
                                        {" "}{fresh.blockedReason === "powersave_requires_awake_idle_observation" ?
                                            "The robot is in power save. Activation remains blocked until an awake idle state is freshly confirmed." :
                                            fresh.blockedReason ? fresh.blockedReason.replace(/_/g, " ") :
                                                "The status prerequisites matched at this read. This does not authorize a setting change."}
                                        {" "}Read at {new Date(fresh.observedAt).toLocaleString()}.
                                    </Alert>
                                )}
                            </Box>
                            {statusPending && !statusError &&
                                <Typography sx={{mt: 2}}>Loading cached CleanGenius settings…</Typography>
                            }

                            {statusError && (
                                <Alert severity="error" sx={{mt: 2}}>
                                    Cannot refresh CleanGenius status. Previously fetched values must not be
                                    interpreted as current.
                                </Alert>
                            )}

                            {!statusError && status && (
                                <>
                                    <Typography variant="subtitle2" sx={{mt: 2}}>
                                        Normal robot state poll
                                    </Typography>
                                    <Typography variant="body2" color="textSecondary">
                                        State: {status.pollHealth.state.replace(/_/g, " ")}
                                        {status.pollHealth.lastAttemptAt ?
                                            ` · Last attempt: ${new Date(status.pollHealth.lastAttemptAt).toLocaleString()}` : ""}
                                    </Typography>
                                    {status.pollHealth.state === "not_started" && (
                                        <Alert severity="info" sx={{mt: 1}}>
                                            No normal state poll has started in this Valetudo process.
                                            This page reads cached data only and does not start a poll.
                                        </Alert>
                                    )}
                                    {status.pollHealth.state === "in_progress" && (
                                        <Alert severity="info" sx={{mt: 1}}>
                                            A normal state poll is in progress; cached readings may not be available yet.
                                        </Alert>
                                    )}
                                    {status.pollHealth.state === "failed" && (
                                        <Alert severity="warning" sx={{mt: 1}}>
                                            The last normal state poll failed. Its error is not exposed here,
                                            and unavailable readings do not establish that the robot is idle.
                                        </Alert>
                                    )}
                                    {status.pollHealth.state === "succeeded" &&
                                        (status.state !== "observed" || status.cachedIdle.state !== "observed") && (
                                        <Alert severity="warning" sx={{mt: 1}}>
                                            A normal poll completed, but one or more cached settings or idle-state
                                            readings are missing, invalid or stale. This does not establish idleness.
                                        </Alert>
                                    )}

                                    {status.state !== "observed" && (
                                        <Alert severity="warning" sx={{mt: 2}}>
                                            {status.state === "stale" ?
                                                "These settings are stale. Their current values are unknown." :
                                                "No valid MIOT 4:50 observation is available yet."}
                                        </Alert>
                                    )}

                                    <Box sx={{mt: 2}}>
                                        <Typography variant="body2" color="textSecondary">
                                            Observation: {status.state}
                                            {status.observedAt ? ` · ${new Date(status.observedAt).toLocaleString()}` : ""}
                                            {status.ageMs !== null ? ` · ${Math.floor(status.ageMs / 1000)} s old` : ""}
                                        </Typography>
                                    </Box>

                                    <Box sx={{
                                        display: "grid",
                                        gridTemplateColumns: {xs: "1fr", md: "1fr 1fr"},
                                        gap: 2,
                                        my: 2
                                    }}>
                                        {DISPLAY_FIELDS.map(({key, title, description}) => {
                                            const setting = status.settings[key];
                                            return (
                                                <Box key={key} sx={{p: 2, border: 1, borderColor: "divider", borderRadius: 1}}>
                                                    <Typography variant="subtitle2">{title}</Typography>
                                                    <Typography sx={{my: 0.5}}>{displaySetting(setting)}</Typography>
                                                    <Typography variant="body2" color="textSecondary">
                                                        {description}
                                                    </Typography>
                                                </Box>
                                            );
                                        })}
                                    </Box>

                                    <Divider sx={{my: 2}}/>
                                    <Typography variant="subtitle1">Raw robot idle gate (read-only)</Typography>
                                    <Typography variant="body2" color="textSecondary" sx={{mb: 1}}>
                                        These numbers come from the existing cached MIOT 4:1 mode and 4:7 task poll,
                                        not from the dock-status indicator. They do not authorize a mode change:
                                        the experimental setter still requires a separate fresh idle check.
                                    </Typography>
                                    <Box sx={{p: 2, border: 1, borderColor: "divider", borderRadius: 1}}>
                                        <Typography>Cached state: {status.cachedIdle.state}</Typography>
                                        <Typography>
                                            Raw mode: {status.cachedIdle.mode ?? "unavailable"}
                                            {" · "}Task status: {status.cachedIdle.taskStatus ?? "unavailable"}
                                        </Typography>
                                        <Typography variant="body2" color="textSecondary">
                                            Cached raw 0/0 pair: {status.cachedIdle.cachedGuardMatch ? "matches 0/0" : "not confirmed"}
                                            {status.cachedIdle.ageMs !== null ?
                                                ` · ${Math.floor(status.cachedIdle.ageMs / 1000)} s old` : ""}
                                        </Typography>
                                    </Box>
                                    <Alert severity="info" sx={{mt: 1}}>
                                        Cached readings are informational only. They cannot authorize a CleanGenius
                                        change; the experimental setter has an independent fresh idle check.
                                    </Alert>

                                    <Divider sx={{my: 2}}/>
                                    <Typography variant="subtitle1">Mop-dock activity</Typography>
                                    <Typography variant="body2" color="textSecondary" sx={{mb: 1}}>
                                        From the existing mop-dock status poll, not from water turbidity or
                                        AI mop-dirtiness messages. History resets when Valetudo restarts.
                                    </Typography>

                                    {status.dockWashActivity.state !== "observed" && (
                                        <Alert severity="warning" sx={{my: 1}}>
                                            Mop-dock activity is {status.dockWashActivity.state}.
                                            No current wash status can be inferred.
                                        </Alert>
                                    )}

                                    <Box sx={{p: 2, border: 1, borderColor: "divider", borderRadius: 1}}>
                                        <Typography variant="subtitle2">Latest dock state</Typography>
                                        <Typography>
                                            {status.dockWashActivity.current.state.replace(/_/g, " ")}
                                            {status.dockWashActivity.current.raw === null ?
                                                "" : ` (raw ${status.dockWashActivity.current.raw})`}
                                        </Typography>
                                        <Typography variant="body2" color="textSecondary" sx={{mt: 1}}>
                                            Recent state changes recorded: {status.dockWashActivity.transitions.length}
                                        </Typography>
                                        {status.dockWashActivity.transitions.slice().reverse().map((entry, index) => (
                                            <Typography variant="caption" display="block"
                                                key={`${entry.at}-${entry.raw}-${index}`}
                                            >
                                                {new Date(entry.at).toLocaleString()} — {entry.state.replace(/_/g, " ")}
                                                {` (raw ${entry.raw})`}
                                            </Typography>
                                        ))}
                                    </Box>
                                    <Alert severity="info" sx={{mt: 2}}>
                                        A cleaning state or repeated transitions does not prove an automatic
                                        rewash, a dirty-mop detection or a CleanGenius decision.
                                    </Alert>

                                    <Divider sx={{my: 2}}/>
                                    <Typography variant="body2">{policy}</Typography>
                                    <Alert severity="info" sx={{mt: 2}}>
                                        Native mop-dirtiness readings, stain classifications and automatic
                                        rewash decisions are not available through this interface.
                                        The settings above must not be interpreted as evidence of those events.
                                    </Alert>
                                </>
                            )}
                        </>
                    )}
                </Box>
            </Box>
        </PaperContainer>
    );
};

export default CleanGeniusStatus;
