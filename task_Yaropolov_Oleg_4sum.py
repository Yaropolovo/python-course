class Solution:
    def fourSum(self, nums: List[int], target: int) -> List[List[int]]:
        output = set()
        nums.sort()

        for first in range(len(nums)-3):
            if nums[first] + nums[first+1] + nums[first+2] + nums[first+3] > target:
                break
            if (nums[first] == nums[first-1]) & (first > 1):
                continue
            for second in range(len(nums)-2)[first+1:]:
                l, r = second+1, len(nums)-1
                while l < r:
                    sum_of_four = nums[first] + nums[second] + nums[l] + nums[r]
                    if sum_of_four < target:
                        l+=1
                    elif sum_of_four > target:
                        r-=1
                    else:
                        output.add(tuple([nums[first], nums[second], nums[l], nums[r]]))
                        l+=1
                        r-=1
                        
        return(list(map(list, output)))
                            