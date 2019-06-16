import numpy as np


class Seller():
    """Seller will produce some amount of supplys per round

    TODO bankruptcy
    """
    def __init__(self, idx, supply_per_round=10,
                 floor_price=20, asking_price=30):
        self.idx = idx
        self.supply_per_round = supply_per_round
        self.to_sell = supply_per_round
        self.floor_price = floor_price
        self.asking_price = asking_price
        self.surplus = 0
        self.total_supply = supply_per_round
        self.sold = 0

    def __repr__(self):
        return f"Sold {self.sold}" \
            + f"/{self.total_supply} " \
            + f"for {self.surplus} profit"

    def round_reset(self, first=False):
        if not first:
            self.total_supply += self.supply_per_round
            self.to_sell = self.supply_per_round


class Buyer():
    """Buyerse will demand some amount of goods per round

    TODO changing tastes
    """
    def __init__(self, idx, demand_per_round=10,
                 ceiling_price=40, asking_price=30):
        self.idx = idx
        self.demand_per_round = demand_per_round
        self.to_buy = demand_per_round
        self.ceiling_price = ceiling_price
        self.asking_price = asking_price
        self.surplus = 0
        self.total_demand = demand_per_round
        self.bought = 0

    def __repr__(self):
        return f"Bought {self.bought}/{self.total_demand} " \
            + f"for {self.surplus} profit"

    def round_reset(self, first=False):
        if not first:
            self.total_demand += self.demand_per_round
            self.to_buy = self.demand_per_round


class Market():
    """This market is a 1-1 randonly matching sellers and buyers (if possible).

    Sellers and buyers adjust their asking price according to
    what happened last round.

    TODO heterogenous agents
    """
    def __init__(self, n_sellers=10, n_buyers=5, duration=1000, **kwargs):
        self.sellers = [Seller(i) for i in range(n_sellers)]
        self.buyers = [Buyer(i) for i in range(n_buyers)]
        self.round = 0
        self.duration = duration

    def __repr__(self):
        return "Current Asking Prices:\n" \
            + f"Sellers: {[seller.asking_price for seller in self.sellers]}\n"\
            + f"Buyers: {[buyer.asking_price for buyer in self.buyers]}\n\n" \
            + f"After {self.round} Rounds:\n" \
            + f"Sellers: {self.sellers}\n" \
            + f"Buyers:  {self.buyers}"

    def trade(self):
        buyers = np.random.permutation(self.buyers)
        sellers = np.random.permutation(self.sellers)

        i = 0
        for seller in sellers:
            # Buyers bought everything they wanted
            # TODO reduce price or decrease quat?
            if all(buyer.to_buy == 0 for buyer in buyers):
                break

            # Out of stock, increase price for next round
            if seller.to_sell == 0:
                seller.asking_price += 1
                continue

            # No more buyers, reduce price for next round
            try:
                buyer = buyers[i]
                while buyer.to_buy == 0:
                    i += 1
                    buyer = buyers[i]

            except IndexError:
                seller.asking_price -= 1
                continue

            # Price was right
            if buyer.asking_price >= seller.floor_price and \
                    seller.asking_price <= buyer.asking_price:
                # TODO how should pricing be determined?
                negotiated_price = \
                    (buyer.asking_price + seller.asking_price)//2
                seller.surplus += (negotiated_price - seller.floor_price)
                buyer.surplus += (buyer.ceiling_price - negotiated_price)
                seller.to_sell -= 1
                seller.sold += 1
                buyer.to_buy -= 1
                buyer.bought += 1
            # Mismatched price,
            else:
                seller.asking_price = max(seller.floor_price,
                                          seller.asking_price - 1)
                buyer.asking_price = min(buyer.ceiling_price,
                                         buyer.asking_price - 1)
            i += 1

    def simulate(self):
        first = True
        for _ in range(self.duration):
            [seller.round_reset(first) for seller in self.sellers]
            [buyer.round_reset(first) for buyer in self.buyers]
            self.trade()
            first = False
            self.round += 1


def main():
    m = Market()
    m.simulate()
    print(m)


if __name__ == "__main__":
    main()
