
// SPDX-License-Identifier: MIT

pragma solidity >=0.6.11;
pragma experimental ABIEncoderV2;

interface IRewardsLogger {
    event DiggPegRewards(
        address indexed beneficiary,
        uint256 response,
        uint256 rate,
        uint256 indexed timestamp,
        uint256 indexed blockNumber
    );
    event RoleAdminChanged(
        bytes32 indexed role,
        bytes32 indexed previousAdminRole,
        bytes32 indexed newAdminRole
    );
    event RoleGranted(
        bytes32 indexed role,
        address indexed account,
        address indexed sender
    );
    event RoleRevoked(
        bytes32 indexed role,
        address indexed account,
        address indexed sender
    );
    event UnlockScheduleModified(
        uint256 index,
        address indexed beneficiary,
        address token,
        uint256 totalAmount,
        uint256 start,
        uint256 end,
        uint256 duration,
        uint256 indexed timestamp,
        uint256 indexed blockNumber
    );
    event UnlockScheduleSet(
        address indexed beneficiary,
        address token,
        uint256 totalAmount,
        uint256 start,
        uint256 end,
        uint256 duration,
        uint256 indexed timestamp,
        uint256 indexed blockNumber
    );

    function DEFAULT_ADMIN_ROLE() external view returns (bytes32);

    function MANAGER_ROLE() external view returns (bytes32);

    function getAllUnlockSchedulesFor(address beneficiary)
        external
        view
        returns (RewardsLogger.UnlockSchedule[] memory);

    function getRoleAdmin(bytes32 role) external view returns (bytes32);

    function getRoleMember(bytes32 role, uint256 index)
        external
        view
        returns (address);

    function getRoleMemberCount(bytes32 role) external view returns (uint256);

    function getUnlockSchedulesFor(address beneficiary, address token)
        external
        view
        returns (RewardsLogger.UnlockSchedule[] memory);

    function grantRole(bytes32 role, address account) external;

    function hasRole(bytes32 role, address account)
        external
        view
        returns (bool);

    function initialize(address initialAdmin_, address initialManager_)
        external;

    function modifyUnlockSchedule(
        uint256 index,
        address beneficiary,
        address token,
        uint256 totalAmount,
        uint256 start,
        uint256 end,
        uint256 duration
    ) external;

    function renounceRole(bytes32 role, address account) external;

    function revokeRole(bytes32 role, address account) external;

    function setDiggPegRewards(
        address beneficiary,
        uint256 response,
        uint256 rate
    ) external;

    function setUnlockSchedule(
        address beneficiary,
        address token,
        uint256 totalAmount,
        uint256 start,
        uint256 end,
        uint256 duration
    ) external;

    function unlockSchedules(address, uint256)
        external
        view
        returns (
            address beneficiary,
            address token,
            uint256 totalAmount,
            uint256 start,
            uint256 end,
            uint256 duration
        );
}

interface RewardsLogger {
    struct UnlockSchedule {
        address beneficiary;
        address token;
        uint256 totalAmount;
        uint256 start;
        uint256 end;
        uint256 duration;
    }
}
