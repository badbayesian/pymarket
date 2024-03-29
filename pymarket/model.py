import numpy as np
import matplotlib.pyplot as plt


class Seller:
    """Seller will produce and try to sell some amount of goods per round to sell.

    TODO bankruptcy
    """

    def __init__(
        self,
        supply_per_round: int = 1,
        floor_price: int = 20,
        asking_price: int = 30,
    ):
        self.supply_per_round = supply_per_round
        self.to_sell = supply_per_round
        self.floor_price = floor_price
        self.asking_price = asking_price
        self.profit = 0
        self.total_supply = supply_per_round
        self.sold = 0

    def __repr__(self):
        return (
            f"Sold {self.sold}"
            + f"/{self.total_supply} "
            + f"for {self.profit} profit"
        )

    def round_reset(self, first: bool = False):
        """Resets suppy for each producer."""
        if not first:
            self.total_supply += self.supply_per_round
            self.to_sell = self.supply_per_round


class Buyer:
    """Buyers will attempt to buy some amount of goods per round.

    TODO changing tastes
    """

    def __init__(
        self,
        demand_per_round: int = 1,
        ceiling_price: int = 40,
        asking_price: int = 30,
    ):
        self.demand_per_round = demand_per_round
        self.to_buy = demand_per_round
        self.ceiling_price = ceiling_price
        self.asking_price = asking_price
        self.profit = 0
        self.total_demand = demand_per_round
        self.bought = 0

    def __repr__(self):
        return (
            f"Bought {self.bought}/{self.total_demand} "
            + f"for {self.profit} profit"
        )

    def round_reset(self, first=False):
        """Resets demand for the round."""
        if not first:
            self.total_demand += self.demand_per_round
            self.to_buy = self.demand_per_round


class Market:
    """This market is a 1-1 randonly matching sellers and buyers (if possible).

    Sellers and buyers adjust their asking price according to
    what happened last round.

    TODO heterogenous agents
    """

    def __init__(
        self,
        n_sellers: int = 10,
        n_buyers: int = 5,
        duration: int = 10,
        rounds: int = 10,
        market_type: str = "uniform",
        **kwargs,
    ):
        """Sets up different types of markets.

        constant -- all buyers and sellers have constant valuation
        uniform -- uniform distribution of buyers and sellers valuation
        normal -- normal distribution of buyers and sellers valuation
        """
        available_markets = ["constant", "uniform", "normal", "custom"]
        if market_type not in available_markets:
            raise NotImplementedError(
                f"{market_type} market type not available"
            )

        self.market_type = market_type
        self.__market = ""
        if self.market_type == "constant":
            self.sellers = np.array([Seller() for _ in range(n_sellers)])
            self.buyers = np.array([Buyer() for _ in range(n_buyers)])
        elif self.market_type == "uniform":
            floor_prices = np.random.randint(10, 30, n_sellers)
            ceiling_prices = np.random.randint(20, 40, n_buyers)
            self.sellers = np.array(
                [
                    Seller(10, floor_prices[i], floor_prices[i] + 10)
                    for i in range(n_sellers)
                ]
            )
            self.buyers = np.array(
                [
                    Buyer(10, ceiling_prices[i], ceiling_prices[i] - 10)
                    for i in range(n_buyers)
                ]
            )
        elif self.market_type == "normal":
            # TODO
            floor_prices = np.round(np.random.normal(20, 10, n_sellers))
            ceiling_prices = np.round(np.random.normal(40, 10, n_buyers))
            self.sellers = np.array(
                [
                    Seller(10, floor_prices[i], floor_prices[i] + 10)
                    for i in range(n_sellers)
                ]
            )
            self.buyers = np.array(
                [
                    Buyer(10, ceiling_prices[i], ceiling_prices[i] - 10)
                    for i in range(n_buyers)
                ]
            )
        self.rounds = rounds
        self.duration = duration

    def __repr__(self):
        # TODO if too many sellers or buyers, condense the information into moments
        # above 10?
        return (
            "Current Asking Prices:\n"
            + f"Sellers: {[seller.asking_price for seller in self.sellers]}\n"
            + f"Buyers: {[buyer.asking_price for buyer in self.buyers]}\n\n"
            + f"After {self.rounds} Rounds:\n"
            + f"Sellers: {self.sellers}\n"
            + f"Buyers:  {self.buyers}"
        )

    def trade(self):
        """Trading per round."""
        for _ in range(self.duration):
            buyers = np.random.permutation(self.buyers)
            sellers = np.random.permutation(self.sellers)
            i = 0
            for seller in sellers:
                # Buyers bought everything they wanted
                # TODO reduce price or decrease quat?
                if all(buyer.to_buy == 0 for buyer in buyers):
                    return "buyers"

                try:
                    buyer = buyers[i]
                    while buyer.to_buy == 0:
                        i += 1
                        buyer = buyers[i]

                except IndexError:
                    continue

                if (buyer.asking_price - seller.asking_price) <= 1:
                    # TODO how should pricing be determined?
                    seller.profit += seller.asking_price - seller.floor_price
                    buyer.profit += buyer.ceiling_price - buyer.asking_price
                    seller.to_sell -= 1
                    seller.sold += 1
                    buyer.to_buy -= 1
                    buyer.bought += 1
                else:
                    pass
                i += 1

            if all([seller.to_sell for seller in self.sellers]):
                return "sellers"
        return "time out"

    def simulate(self):
        """Simulates market until ending condition."""
        max_price = np.array(
            [buyer.asking_price for buyer in self.buyers]
        ).max()
        min_price = np.array(
            [seller.asking_price for seller in self.sellers]
        ).min()

        first = True
        for _ in range(self.rounds):
            [seller.round_reset(first) for seller in self.sellers]
            [buyer.round_reset(first) for buyer in self.buyers]
            self.__market = self.trade()
            for seller in self.sellers:
                if seller.to_sell > 0:
                    seller.asking_price = max(
                        seller.floor_price, seller.asking_price - 1
                    )
                elif max_price == seller.asking_price:
                    pass
                elif self.__market == "sellers":
                    seller.asking_price += 1
            for buyer in self.buyers:
                if buyer.to_buy > 0:
                    buyer.asking_price = min(
                        buyer.ceiling_price, buyer.asking_price + 1
                    )
                elif min_price == buyer.asking_price:
                    pass
                elif self.__market == "buyers":
                    buyer.asking_price -= 1
            first = False

    def plot(self):
        """Plots stuff TODO"""
        buyer = sorted(
            [(buyer.ceiling_price, buyer.bought) for buyer in self.buyers],
            key=lambda x: x[0],
        )
        seller = sorted(
            [(seller.floor_price, seller.sold) for seller in self.sellers],
            key=lambda x: x[0],
            reverse=True,
        )
        print(buyer)
        print(seller)


def main():
    m = Market(
        n_sellers=10,
        n_buyers=5,
        market_type="uniform",
        rounds=1,
        duration=1000,
    )
    m.simulate()
    print(m)


if __name__ == "__main__":
    main()
