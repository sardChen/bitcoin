import com.google.common.util.concurrent.FutureCallback;
import com.google.common.util.concurrent.Futures;
import com.google.common.util.concurrent.MoreExecutors;
import org.bitcoinj.core.*;
import org.bitcoinj.net.discovery.DnsDiscovery;
import org.bitcoinj.params.TestNet3Params;
import org.bitcoinj.store.BlockStoreException;
import org.bitcoinj.store.SPVBlockStore;
import org.bitcoinj.wallet.Wallet;
import org.bitcoinj.wallet.listeners.WalletCoinsReceivedEventListener;

import java.io.File;

public class BitCoinHelloWorld implements WalletCoinsReceivedEventListener {

    public static void main(String[] args) {
        BitCoinHelloWorld demo = new BitCoinHelloWorld();

        demo.run();
    }

    private void run() {
        try {
            init();

            System.out.println("Waiting for coins...");

            while (true) {
                Thread.sleep(20);
            }
        } catch (BlockStoreException | InterruptedException | InsufficientMoneyException e) {
            e.printStackTrace();
        }
    }

    private void init() throws BlockStoreException, InsufficientMoneyException {
        NetworkParameters params  = TestNet3Params.get();

        ECKey key = new ECKey();
        System.out.println("We created a new key:\n" + key);

        Address addressFromKey = key.toAddress(params);
        System.out.println("Public Address generated: " + addressFromKey);

        System.out.println("Private key is: " + key.getPrivateKeyEncoded(params).toString());

        Wallet wallet = new Wallet(params);
        wallet.importKey(key);

        File blockFile = new File("/tmp/bitcoin-blocks");
        SPVBlockStore blockStore = new SPVBlockStore(params, blockFile);

        BlockChain blockChain = new BlockChain(params, wallet, blockStore);
        PeerGroup peerGroup = new PeerGroup(params, blockChain);
        peerGroup.addPeerDiscovery(new DnsDiscovery(params));
        peerGroup.addWallet(wallet);

        System.out.println("Start peer group");
        peerGroup.start();

        System.out.println("Downloading block chain");
        peerGroup.downloadBlockChain();
        System.out.println("Block chain downloaded");

        wallet.addCoinsReceivedEventListener(this);

        final Coin amountToSend = Coin.valueOf(10, 0);
        Address toAddress = Address.fromBase58(params, "miVBD7TZ6XVqy2mJNGM9D7xgVAgcrv48Ys");
        final Wallet.SendResult sendResult = wallet.sendCoins(peerGroup, toAddress, amountToSend);
        sendResult.broadcastComplete.addListener(new Runnable() {
            @Override
            public void run() {
                System.out.println("Coins had Sent to miVBD7TZ6XVqy2mJNGM9D7xgVAgcrv48Ys! Transaction hash is " +
                        sendResult.tx.getHashAsString());
            }
        }, MoreExecutors.sameThreadExecutor());
    }


    @Override
    public void onCoinsReceived(final Wallet wallet, final Transaction transaction, Coin prevBalance, Coin newBalance) {
        final Coin value = transaction.getValueSentToMe(wallet);

        System.out.println("Received tx for " + value.toFriendlyString() + ": " + transaction);

        System.out.println("Previous balance is " + prevBalance.toFriendlyString());

        System.out.println("New estimated balance is " + newBalance.toFriendlyString());

        System.out.println("Coin received, wallet balance is :" + wallet.getBalance());

        Futures.addCallback(transaction.getConfidence().getDepthFuture(1), new FutureCallback<TransactionConfidence>() {
            public void onSuccess(TransactionConfidence result) {
                System.out.println("Transaction confirmed, wallet balance is :" + wallet.getBalance());
            }

            public void onFailure(Throwable t) {
                t.printStackTrace();
            }
        });
    }
}