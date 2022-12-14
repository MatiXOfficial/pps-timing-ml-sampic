import numpy as np
from uproot import ReadOnlyDirectory


class WaveformData:
    def __init__(self, series: np.ndarray, t0: float) -> None:
        self.series = series
        self.t0 = t0
        self.t_cfd: None | float = None
        self.true_t_cfd: None | float = None

    @classmethod
    def from_channel_data(cls, channel_data: ReadOnlyDirectory):
        series = np.array(channel_data['wavCal'].values())
        series[1] = -series[1] + 1  # revert
        t0 = channel_data['t0'].members['fVal']
        return cls(series, t0)

    def get_metadata_str(self) -> str:
        return {
            't0': self.t0,
            't_cfd': self.t_cfd
        }.__str__()


class EventData:
    def __init__(self, planes: dict[int, dict[int, WaveformData]]) -> None:
        self.planes = planes
        self.t_cfd_average = None

    @classmethod
    def from_event_data(cls, event_data: ReadOnlyDirectory):
        planes = {}
        for plane_key, plane_data in event_data.items(recursive=False):
            plane_name = int(plane_key[6:-2])
            planes[plane_name] = {}
            for channel_key, channel_data in plane_data.items(recursive=False):
                channel_name = int(channel_key[8:-2])
                planes[plane_name][channel_name] = WaveformData.from_channel_data(channel_data)
        return cls(planes)

    def __str__(self) -> str:
        return {f'plane {plane_name}': {f'channel {channel_name}': f't0: {wav_data.t0}' for channel_name, wav_data in
                                        plane_data.items()} for plane_name, plane_data in self.planes.items()}.__str__()

    def get_metadata_dict(self) -> dict[str, dict[str, str]]:
        return {
            f'plane {plane_name}': {f'channel {channel_name}': wav_data.get_metadata_str() for channel_name, wav_data in
                                    plane_data.items()} for plane_name, plane_data in self.planes.items()}

    def get_plane_count(self) -> int:
        return len(self.planes)

    def get_hit_count(self) -> int:
        return sum(len(channels) for channels in self.planes.values())

    def get_all_waveforms(self) -> list[tuple[int, int, WaveformData]]:
        wavs = []
        for plane, channels in self.planes.items():
            for channel, wav_data in channels.items():
                wavs.append((plane, channel, wav_data))

        return wavs

    def remove_channel(self, plane: int, channel: int) -> None:
        del self.planes[plane][channel]
        if not self.planes[plane]:
            del self.planes[plane]
