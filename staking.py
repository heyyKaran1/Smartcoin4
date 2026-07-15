import time
from typing import Dict, List


class StakingPool:
    def __init__(self, apy: float = 10.0):
        self.apy = apy  # Annual Percentage Yield
        self.stakes: Dict[str, Dict] = {}  # address -> stake info
        self.total_staked = 0.0

    def stake(self, address: str, amount: float) -> bool:
        if amount <= 0:
            return False

        if address in self.stakes:
            # Add to existing stake
            self.stakes[address]['amount'] += amount
        else:
            # Create new stake
            self.stakes[address] = {
                'amount': amount,
                'staked_at': time.time(),
                'last_claim': time.time(),
                'total_rewards': 0
            }

        self.total_staked += amount
        return True

    def unstake(self, address: str, amount: float) -> bool:
        if address not in self.stakes:
            return False

        stake = self.stakes[address]
        if stake['amount'] < amount:
            return False

        # Calculate pending rewards before unstaking
        rewards = self.calculate_rewards(address)
        stake['total_rewards'] += rewards
        stake['last_claim'] = time.time()

        # Unstake
        stake['amount'] -= amount
        self.total_staked -= amount

        # Remove if no more stake
        if stake['amount'] == 0:
            del self.stakes[address]

        return True

    def calculate_rewards(self, address: str) -> float:
        if address not in self.stakes:
            return 0

        stake = self.stakes[address]
        time_staked = time.time() - stake['last_claim']  # in seconds
        years_staked = time_staked / (365 * 24 * 60 * 60)

        # Reward = Staked Amount × APY × Time
        reward = stake['amount'] * (self.apy / 100) * years_staked
        return reward

    def claim_rewards(self, address: str) -> float:
        if address not in self.stakes:
            return 0

        rewards = self.calculate_rewards(address)
        self.stakes[address]['last_claim'] = time.time()
        self.stakes[address]['total_rewards'] += rewards

        return rewards

    def get_stake_info(self, address: str) -> Dict:
        if address not in self.stakes:
            return {
                'staked': 0,
                'pending_rewards': 0,
                'total_rewards': 0,
                'apy': self.apy
            }

        stake = self.stakes[address]
        pending = self.calculate_rewards(address)

        return {
            'staked': stake['amount'],
            'pending_rewards': pending,
            'total_rewards': stake['total_rewards'],
            'staked_at': stake['staked_at'],
            'apy': self.apy
        }

    def get_pool_stats(self) -> Dict:
        return {
            'total_staked': self.total_staked,
            'stakers_count': len(self.stakes),
            'apy': self.apy
        }
