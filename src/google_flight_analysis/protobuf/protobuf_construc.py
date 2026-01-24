import base64
import src.google_flight_analysis.protobuf.schema_pb2 as PB
from typing import Any, List, Optional, TYPE_CHECKING, Literal
import re

if TYPE_CHECKING:
    PB: Any


class FlightData:
    """Represents flight data.

    Args:
        date (str): Date.
        from_airport (str): Departure (airport). Where from?
        to_airport (str): Arrival (airport). Where to?
        max_stops (int, optional): Maximum number of stops. Default is None.
    """

    __slots__ = ("date", "from_airport", "to_airport", "max_stops")
    date: str
    from_airport: List[str]
    to_airport: List[str]
    max_stops: Optional[int]

    def __init__(
        self,
        *,
        date: str,
        from_airport: List[str],
        to_airport: List[str],
        max_stops: Optional[int] = None,
    ):
        self.date = date
        self.from_airport = from_airport
        self.to_airport = to_airport
        self.max_stops = max_stops

    def attach(self, info: PB.Info) -> None:  # type: ignore
        data = info.data.add()
        data.date = self.date
        for airp in self.from_airport:
            airport = data.from_flight.add()
            airport.airport = airp
            # Set code_type: 1 if airp code is a three-letter [A-Z] string, else 4
            if re.fullmatch(r"[A-Z]{3}", airp):
                code_type = 1
            else:
                code_type = 2  # Supposing it's a city
            airport.TYPE = code_type

        for airp in self.to_airport:
            airport = data.to_flight.add()
            airport.airport = airp
            # Set code_type: 1 if airp code is a three-letter [A-Z] string, else 4
            if re.fullmatch(r"[A-Z]{3}", airp):
                code_type = 1
            else:
                code_type = 4  # Supposing it's a country
            airport.TYPE = code_type

        if self.max_stops is not None:
            data.max_stops = self.max_stops

    def __repr__(self) -> str:
        return (
            f"FlightData(date={self.date!r}, "
            f"from_airport={self.from_airport}, "
            f"to_airport={self.to_airport}, "
            f"max_stops={self.max_stops})"
        )


class Passengers:
    def __init__(
        self,
        *,
        adults: int = 1
    ):
        self.adults = adults
        self.pb = []
        self.pb += [PB.Passenger.ADULT for _ in range(adults)]

        self.passengers = {
            "unknown": PB.Passenger.UNKNOWN_PASSENGER,
            "adults": PB.Passenger.ADULT,
            "children": PB.Passenger.CHILD,
            "infants_in_seat": PB.Passenger.INFANT_IN_SEAT,
            "infants_on_lap": PB.Passenger.INFANT_ON_LAP,
        }["adults"]  # Default to adults

    def attach(self, info: PB.Info) -> None:  # type: ignore
        for p in self.pb:
            info.passengers.append(p)

    def __repr__(self) -> str:
        return f"{self.adults} adults"


class TFSData:
    """``?tfs=`` data. (internal)

    Use `TFSData.from_interface` instead.
    """

    def __init__(
        self,
        *,
        search_mode: int,  # 2: flights mode, 3: explore mode
        flight_data: List[FlightData],
        seat: PB.Seat,  # type: ignore
        trip: PB.Trip,  # type: ignore
        passengers: Passengers,
        max_stops: Optional[int] = None,  # Add max_stops to the constructor
    ):
        self.flight_data = flight_data
        self.seat = seat
        self.trip = trip
        self.passengers = passengers
        self.max_stops = max_stops  # Store max_stops
        self.search_mode = search_mode

    def pb(self) -> PB.Info:  # type: ignore
        info = PB.Info()
        info.seat = self.seat
        info.trip = self.trip
        info.metadata_1 = 28
        info.metadata_2 = self.search_mode
        info.search_mode = 1  # Using specific date search mode

        # if self.search_mode == 2:
        #     self.passengers.attach(info)
        # else:
        #     info.passengers = self.passengers.passengers
        if True:
            info.passengers = self.passengers.passengers

        for fd in self.flight_data:
            fd.attach(info)

        # If max_stops is set, attach it to all flight data entries
        if self.max_stops is not None:
            for flight in info.data:
                flight.max_stops = self.max_stops

        return info

    def to_string(self) -> bytes:
        return self.pb().SerializeToString()

    def as_b64(self) -> bytes:
        return base64.b64encode(self.to_string())

    @staticmethod
    def from_interface(
        *,
        explore_mode = bool,
        flight_data: List[FlightData],
        trip: Literal["round-trip", "one-way", "multi-city"],
        passengers: Passengers,
        seat: Literal["economy", "premium-economy", "business", "first"],
        max_stops: Optional[int] = None,  # Add max_stops to the method signature
    ):
        """Use ``?tfs=`` from an interface.

        Args:
            flight_data (list[FlightData]): Flight data as a list.
            trip ("one-way" | "round-trip" | "multi-city"): Trip type.
            passengers (Passengers): Passengers.
            seat ("economy" | "premium-economy" | "business" | "first"): Seat.
            max_stops (int, optional): Maximum number of stops.
        """
        trip_t = {
            "round-trip": PB.Trip.ROUND_TRIP,
            "one-way": PB.Trip.ONE_WAY,
            "multi-city": PB.Trip.MULTI_CITY,
        }[trip]

        seat_t = {
            "economy": PB.Seat.ECONOMY,
            "premium-economy": PB.Seat.PREMIUM_ECONOMY,
            "business": PB.Seat.BUSINESS,
            "first": PB.Seat.FIRST,
        }[seat]

        search_mode = 3 if explore_mode else 2

        return TFSData(
            search_mode=search_mode,
            flight_data=flight_data,
            seat=seat_t,
            trip=trip_t,
            passengers=passengers,
            max_stops=max_stops  # Pass max_stops into TFSData
        )

    def __repr__(self) -> str:
        return f"TFSData(flight_data={self.flight_data!r}, max_stops={self.max_stops!r})"

