import React from "react";
import {Alert, Box, Chip, Divider, Typography} from "@mui/material";
import {Insights as CleanGeniusIcon} from "@mui/icons-material";
import {
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
        title: "Stain Identification setting",
        description: "Whether StainIdentify is configured on; not a live stain detection."
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

    const policy = status?.valetudoPolicy === "experimental_controls_opted_in" ?
        "Experimental writable CleanGenius quirks are opted in. This page remains read-only." :
        "Valetudo normally disables positive SmartHost settings to protect manual controls. " +
        "A reported setting may not be the effective native cleaning mode.";

    return (
        <PaperContainer>
            <Box sx={{width: "100%"}}>
                <DetailPageHeaderRow
                    title="CleanGenius Status"
                    icon={<CleanGeniusIcon/>}
                    onRefreshClick={supported ? () => { void refetch(); } : undefined}
                    isRefreshing={statusFetching}
                />

                <Box sx={{p: 2}}>
                    <Chip label="Read-only" variant="outlined" size="small"/>
                    <Typography variant="body2" color="textSecondary" sx={{mt: 1}}>
                        X40 Ultra native settings observed through the existing MIOT 4:50 state poll.
                        No cleaning commands, native service calls or sensor recordings are made by this page.
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
