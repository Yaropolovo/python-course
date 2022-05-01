class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        output = set()
        nums.sort()

        for i in range(len(nums)-2):
            if nums[i] > 0:
                break
            if (nums[i] == nums[i-1]) & (i > 0):
                continue
            l, r = i+1, len(nums)-1 
            while l<r:
                current_sum = nums[i]+nums[l]+nums[r]
                if current_sum == 0:
                    new_val = tuple([nums[i],nums[l],nums[r]])
                    output.add(new_val)
                    l+=1
                    r-=1
                elif current_sum < 0:
                    l+=1
                else:
                    r-=1
        return(map(list, output))