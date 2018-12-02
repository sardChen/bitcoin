import com.google.common.util.concurrent.MoreExecutors;
import org.bitcoinj.core.*;
import org.bitcoinj.params.TestNet3Params;
import org.bitcoinj.store.BlockStoreException;
import org.bitcoinj.store.SPVBlockStore;
import org.bitcoinj.wallet.Wallet;

import java.io.File;

public class SendBitCoin {
    public static void main(String args[]) throws InsufficientMoneyException, BlockStoreException {
        NetworkParameters params  = TestNet3Params.get();
        Wallet wallet = new Wallet(params);
        File blockFile = new File("/tmp/bitcoin-blocks");
        SPVBlockStore blockStore = new SPVBlockStore(params, blockFile);
        BlockChain blockChain = new BlockChain(params, wallet, blockStore);
        PeerGroup peerGroup = new PeerGroup(params, blockChain);

        final Coin amountToSend = Coin.valueOf(10, 0);
        Address toAddress = Address.fromBase58(params, "n2eMqTT929pb1RDNuqEnxdaLau1rxy3efi");
        final Wallet.SendResult sendResult = wallet.sendCoins(peerGroup, toAddress, amountToSend);
        sendResult.broadcastComplete.addListener(new Runnable() {
            @Override
            public void run() {
                System.out.println("Coins Sent! Transaction hash is " + sendResult.tx.getHashAsString());
            }
        }, MoreExecutors.sameThreadExecutor());
    }
}
