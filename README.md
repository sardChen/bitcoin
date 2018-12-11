# bitcoin

## 系统架构图
![image](https://github.com/131250106/bitcoin/blob/master/img/design.png)

## 系统模块设计图
![image](https://github.com/131250106/bitcoin/blob/master/img/module.png)

## 创世节点启动流程图
![image](https://github.com/131250106/bitcoin/blob/master/img/initialnode.png)

## 其它节点启动时序图
![image](https://github.com/131250106/bitcoin/blob/master/img/time.png)

## POW共识算法设计与实现
1. 所有节点启动完毕后，新开一个线程，执行挖矿逻辑
2. 某个节点一旦挖到某个block后，从transaction池中拉取TX，验证并放入新的block中
3. 该节点将new block 广播出去后，继续挖下一个区块
4. 某一节点一旦收到某个new block，立即发送一个信号量，停止当前挖矿行为
5. 验证该收到的new block
	5.1 如果验证通过，则将该new block添加到自己的链上
	5.2 验证不通过：
		5.2.1 从自己的routing table中的所有邻居节点拉取区块链
		5.2.2 逐个与自身区块链进行对比
			5.2.2.1 若区块链比自己的长，则用该区块链覆盖掉自己的链
			5.2.2.2 若区块链与自己的一样长，寻找fork分支点，进行fork操作

## 不同算力攻击成功概率
//TODO

## 不同带块分叉概率
//TODO

## BGD劫持 or eclipse攻击
//TODO

## POS共识算法设计与实现
//TODO

## PBFT共识算法设计与实现
//TODO

